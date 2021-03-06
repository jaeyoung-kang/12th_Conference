# -*- coding: utf-8 -*-
"""model.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qdf1uymWklV0E9Uav2D3-CeP1cDMKrFB
"""

#!pip install git+https://github.com/naver/kor2vec.git


import torch
from torch.utils.data import Dataset, DataLoader
from torch import nn
from torchvision import transforms
import torchvision.datasets as datasets
from PIL import Image
import torchvision.models as models # 임베딩 모델
import torchvision
import torch.optim as optim
import pickle
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import euclidean_distances
import pandas as pd
import numpy as np
import os
from kor2vec import Kor2Vec # Kor2Vec import

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

#경로
#location = "/content/drive/MyDrive/14,15 추천컨퍼런스/"
#df = pd.read_csv(location + 'final_df_link.csv')
#kor2Vec_location = location+"show_and_tell_final_model/embedding_final"
location = "main/model/"
df = pd.read_csv(location + 'final_df_link_j.csv')
kor2Vec_location = location + "show_and_tell_final_model/embedding_final"

# show_and_tell hyperparameter 조정
embed_size_tune = 64
batch_size_tune = 64
seq_length = 20
drop_out_per = 0.5
learning_rate=0.001
epoch_time=5

class SuperLightMobileNet(nn.Module):
    def __init__(self, num_classes=1000):
        super(SuperLightMobileNet, self).__init__()

        def conv_bn(inp, oup, stride):
            return nn.Sequential(
                nn.Conv2d(inp, oup, 3, stride, 1, bias=False),
                nn.BatchNorm2d(oup),
                nn.ReLU(inplace=True)
            )

        def conv_dw(inp, oup, stride):
            return nn.Sequential(
                nn.Conv2d(inp, inp, 3, stride, 1, groups=inp, bias=False),
                nn.BatchNorm2d(inp),
                nn.ReLU(inplace=True),
    
                nn.Conv2d(inp, oup, 1, 1, 0, bias=False),
                nn.BatchNorm2d(oup),
                nn.ReLU(inplace=True),
            )
        self.num_classes = num_classes
        self.model = nn.Sequential(
            conv_bn(  3,  32, 2), 
            conv_dw( 32,  64, 1),
            conv_dw( 64, 128, 2)
        )
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(128, self.num_classes)

    def forward(self, x):
        x = self.model(x)
        x = self.gap(x)
        x = x.view(-1, 128)
        x = self.fc(x)
        return x

    def give_embedding(self, x): 
        x = self.model(x)
        x = self.gap(x)
        x = x.view(-1, 128)
        return x

class Decoder(nn.Module):
    def __init__(self, output_dim, emb_dim, hid_dim, dropout):
        super().__init__()
        self.hid_dim = hid_dim
        self.output_dim = output_dim
        self.embedding = nn.Embedding(output_dim, emb_dim)
        self.rnn = nn.GRU(emb_dim + hid_dim, hid_dim)
        self.fc_out = nn.Linear(emb_dim + hid_dim * 2, output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, input, hidden, context):
        embedded = self.dropout(input)
        emb_con = torch.cat((embedded, context), dim = 2)
        output, hidden = self.rnn(emb_con, hidden)
        output = torch.cat((embedded.squeeze(0), hidden.squeeze(0), context.squeeze(0)), 
                           dim = 1)
        prediction = self.fc_out(output)
        return prediction.unsqueeze(0), hidden

class Net(nn.Module):
    """
    신경망 파일
    hidden_size : kor2vec의 embedding size 로 맞춰야 합니다.
    """
    def __init__(self, seq_len = seq_length, embedding_size = embed_size_tune, hidden_size = embed_size_tune):
        super(Net, self).__init__()
        self.seq_len = seq_len
        self.embedding_size = embedding_size
        self.hidden_size = hidden_size
        self.resnet = models.resnet18(pretrained=True)
        self.decoder = Decoder(embed_size_tune, self.embedding_size, self.hidden_size, drop_out_per)
        self.kor2vec = Kor2Vec.load(kor2Vec_location)

    # resNet의 모든 파라미터를 잠그고 마지막 레이어만 얼리지 않고 사용합니다.
        for param in self.resnet.parameters():
            param.requires_grad = False
        self.resnet.fc = nn.Linear(512, embed_size_tune) # 마지막 레이어만 다시 사용합니다.

        # kor2vec의 모든 파라미터를 얼립니다.
        for param in self.kor2vec.parameters():
            param.requires_grad = False

    def forward(self, x):
        batch_size = x.shape[0]
        x = self.resnet(x).reshape(1,batch_size,self.hidden_size) # resnet 통과 output: (batch, hidden) torch.Size([64, 1, 3, 224, 224])
        hidden = x # lstm의 초기 셀 값은 resNet의 출력입니다.
        outputs = torch.zeros(self.seq_len, batch_size, self.embedding_size).to(device) # sequence를 저장하기 위한 빈 배열

        # <sos> 를 시작 토큰으로 설정합니다.
        output = self.kor2vec.embedding('<sos>').unsqueeze(0).repeat(1, batch_size, 1).to(device)

        # seq 결과물을 lstm의 입력으로 사용하여 seq_len 만큼 반복하여 저장합니다.
        for t in range(0, self.seq_len):
            output, hidden = self.decoder(output, hidden, x ) 
            outputs[t] = output
        
        return outputs.reshape(batch_size, self.seq_len, self.embedding_size) # shape: (15, batch_size, 1000)


    def give_embedding(self, x):
        batch_size = x.shape[0]
        x = self.resnet(x).reshape(1,batch_size,self.hidden_size) # resnet 통과 output: (batch, hidden)[1,64,hidden]
        
        hidden = x # lstm의 초기 셀 값은 resNet의 출력입니다.
        outputs = torch.zeros(self.seq_len, batch_size, self.embedding_size).to(device) # sequence를 저장하기 위한 빈 배열
        
        # <sos> 를 시작 토큰으로 설정합니다.
        output = self.kor2vec.embedding('<sos>').unsqueeze(0).repeat(1, batch_size, 1).to(device)

        # seq 결과물을 lstm의 입력으로 사용하여 seq_len = 15 만큼 반복하여 저장합니다.
        output, hidden = self.decoder(output, hidden, x )  
        return hidden

    def give_resnet_embedding(self, x): 
        batch_size = x.shape[0]
        x = self.resnet(x).reshape(1,batch_size,self.hidden_size) # resnet 통과 output: (batch, hidden)

        hidden =x # lstm의 초기 셀 값은 resNet의 출력입니다.
        return hidden

    # model.train() 을 위해 메소드 오버라이딩
    def train(self, mode=True):  
        self.training = mode
        for module in self.children():
            if module != self.kor2vec:
                module.train(mode)
        return self

    # model.eval() 을 위한 설정
    def eval(self, mode=False): 
        # self.training = mode
        for module in self.children():
            if module != self.kor2vec:
                module.train(mode)
        return self

class ImageDataset(Dataset):
    """
    root_dir : 이미지 파일이 있는 경로
    captions_file : 이미지 제목-리뷰가 포함된 데이터프레임
    transform : 이미지를 텐서로 변환할 때 transform (optional)
    """
    def __init__(self, img_dir, df, transform=None):
        self.root_dir = img_dir
        self.transform = transform
        self.df = df
        self.imgs = self.df['cafe_image_name'] # 이미지 파일 경로
        self.labels = self.df["Label"] # 리뷰 데이터
        
    def __len__(self):
        return len(self.df)
    
    # 이미지, 텍스트를 불러 오는 메소드
    # transform을 선언하면 임베딩 벡터와 1개 배치로 반환하며, 선언하지 않으면 이미지와 스트링 형태의 캡션을 반환합니다.
    def __getitem__(self,idx):
        label = self.labels[idx] # target caption
        img_name = self.imgs[idx] # 이미지 이름 파일 불러오기
        img_location = os.path.join(self.root_dir,img_name) # 실제로 이미지 오픈
        img = Image.open(img_location).convert("RGB")
        
        # transform이 있다면 실시 후 배치화(1 차원 추가)
        if self.transform is not None:
            img = self.transform(img)
        return img, label

class CaptionDataset(Dataset):
    """
    root_dir : 이미지 파일이 있는 경로
    captions_file : 이미지 제목-리뷰가 포함된 데이터프레임
    transform : 이미지를 텐서로 변환할 때 transform (optional)
    """
    def __init__(self, img_dir, caption_df, transform=None):
        self.root_dir = img_dir
        self.transform = transform
        self.df = caption_df
        self.imgs = self.df['imgname_123'] # 이미지 파일 경로
        self.captions = self.df["summary_text"] # 리뷰 데이터
        self.kor2vec = Kor2Vec.load(kor2Vec_location) # Kor2Vec 로드
        
    def __len__(self):
        return len(self.df)
    
    # 이미지, 텍스트를 불러 오는 메소드
    # transform을 선언하면 임베딩 벡터와 1개 배치로 반환하며, 선언하지 않으면 이미지와 스트링 형태의 캡션을 반환합니다.
    def __getitem__(self,idx):
        caption = self.captions[idx] # target caption
        img_name = self.imgs[idx] # 이미지 이름 파일 불러오기
        img_location = os.path.join(self.root_dir,img_name) # 실제로 이미지 오픈
        img = Image.open(img_location).convert("RGB")
        
        # transform이 있다면 실시 후 배치화(1 차원 추가)
        if self.transform is not None:
            img = self.transform(img)
            # 정답 임베딩 데이터 
            caption = self.kor2vec.embedding(caption, seq_len=seq_length)

        return img, caption

def classification():
    model = SuperLightMobileNet(5).to(device)
    model.load_state_dict(torch.load(location+'final_0706_emb_total_model_light9_0.001_10.pth', map_location=device))
    model.eval()  
    return model

def caption():
    model = Net()
    model.to(device)
    model.eval()  
    model.load_state_dict(torch.load(location+'show_and_tell_final_model/show_and_tell_final.pt', map_location=device))
    return model

def image_plus(df, img_dir, img_name):

    if df["cafe_image_name"].isin([img_name]).any():
        target_idx=df[df["cafe_image_name"]==img_name].index.to_list()[0]

        with open(location+'tag_review_embeddings_0710.pickle', 'rb') as f:
                tag_review_embeddings = pickle.load(f)

        dist_mtx = euclidean_distances(tag_review_embeddings,tag_review_embeddings)

        plt.imshow(Image.open(location+ 'img_final/MND COFFEE_2.jpg'))
        plt.show()
        # 가장 가까운 것의 인덱스를 제공해준다
        # ex target_idx가 200이라면, 첫 인덱스는 200

        close_list = dist_mtx[target_idx].argsort()[1:6]

        '''
        print("가장 가까운 이미지")
        print("======================")
        # target을 포함해 target과 가장 가까운 것 10개
        for i, idx in enumerate(close_list):
            img, rev = reveiw_train_data[idx]
            print(f"{i}, {rev}, distance : {dist_mtx[target_idx][idx]}")
            plt.imshow(img)
        plt.show()
        '''
        return close_list
        

    else:
        print('######## else ########')
        transform = transforms.Compose(
            [transforms.ToTensor(), # 텐서로 변형
             transforms.Resize(224), # 사이즈 조절
             transforms.CenterCrop(224), # 가로와 세로 중 안 맞는 곳 자르기
             transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    
        reveiw_train_data = CaptionDataset(location+'img_final', df, transform=None)

        mobile_net_model = classification()
        show_and_tell_model = caption()
        
        # image 사이즈 변경
        #image=Image.open(img_dir)
        #img = Image.open(img_name).convert("RGB")
        
        #img = Image.open(location+ 'img_final/MND COFFEE_2.jpg').convert("RGB")
        img = Image.open(img_name).convert("RGB")
        img = transform(img)
        img = img.unsqueeze(0)

        # review embedding
        img = img.to(device)
        review_embed = show_and_tell_model.give_embedding(img).cpu().detach().numpy().reshape(-1, 64)

        # tag embedding
        tag_embed = mobile_net_model.give_embedding(img).cpu().detach().numpy()

        # finale embedding
        final_embed = np.concatenate((tag_embed, review_embed), axis=1)

        # tag + review 임베딩 로드
        with open(location+'tag_review_embeddings_0710.pickle', 'rb') as f:
            tag_review_embeddings = pickle.load(f)

        # 최종 embedding concat
        final_embedding = np.concatenate((tag_review_embeddings, final_embed), axis=0)

        #거리 계산
        dist_mtx = euclidean_distances(final_embedding,final_embedding)

        # plt.imshow(Image.open(img_dir+img_name))
        # plt.show()
        target_idx = len(final_embedding)-1

        # 가장 가까운 것의 인덱스를 제공해준다
        # ex target_idx가 200이라면, 첫 인덱스는 200
        close_list = dist_mtx[target_idx].argsort()[1:6]

        return close_list

if __name__ == "__main__": # 별도 실행을 위해 남겨놓음
    transform = transforms.Compose(
        [transforms.ToTensor(), # 텐서로 변형
         transforms.Resize(224), # 사이즈 조절
         transforms.CenterCrop(224), # 가로와 세로 중 안 맞는 곳 자르기
         transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    # reveiw_train_data = CaptionDataset(location+'img_final', df, transform=None)

    # mobile_net_model = classification()
    # show_and_tell_model = caption()
    #image_plus(df,location+'img_final/', '&meal_1.jpg')
    
    #print(location)
    
    #close_list = image_plus(df, location+'img_final/', location+ 'img_final/36.5도여름_3.jpg')
    #close_list = image_plus(df, location+'img_final/', location+ 'img_final/MND COFFEE_2.jpg')
    close_list = image_plus(df, location+'img_final/', 'MND COFFEE_2.jpg')
    
    #print(df.loc[close_list, :])
    
    data_dict = {}
    for index in close_list:
        data_dict[index] = df.loc[index, :]
    
    #print(data_dict)
    #print(close_list)


