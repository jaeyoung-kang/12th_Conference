# 카페인(Cafe-in)
### 너는 내 취향저격, 이미지 기반 카페 추천시스템
2021.07.17 **[제 12회 투빅스 컨퍼런스]** 발표작
![Cafe-In 일단 완성 - 수정_1](https://user-images.githubusercontent.com/67720742/125875074-9096eb63-dd38-4423-b3fd-ae7f4d504121.png)
- **카페 이미지**를 넣으면, 유사한 느낌의 **카페를 추천**해주는 서비스입니다.
- **이미지뿐만 아니라** 기존 카페 이용고객들의 **리뷰**와 **태그 데이터**를 활용합니다.
- 다이닝코드 데이터 기반으로 진행하였으며, 상업적으로 이용할 의도가 전혀 없음을 밝힙니다.

<br>

## Structure

```python
카페인
├── README.md
├── data_preprocessing
│   ├───crawling.py
│   └───preprocess.py
│   
├── final_model
│   ├── show_and_tell
│     ├───show_and_tell_proprecess.py
│     ├───show_and_tell_embedding.py
│     ├───show_and_tell_model.py
│     ├───show_and_tell_train.py
│     └───similarity_result.py
│   ├── tag   
│     ├───tag_dataloader.py
│     ├───tag_embedding.py
│     ├───tag_mobilenet.py
│     └───tag_train.py

```
**crawling.py** : 다이닝코드 데이터 크롤링 코드입니다.<br><br>
**preprocess.py** : 리뷰데이터 토크나이즈 및 데이터 클렌징 코드입니다. <br><br>
**show_and_tell_model.py** : show and tell 모델이 정의된 코드입니다. <br><br>
**show_and_tell_proprecess.py** : 데이터 전처리 및 kor2vec embedding을 만들고 저장하고 show and tell 모델에 적용시키기 위한 dataloader를 만드는 코드입니다. <br><br>
**show_and_tell_train.py** : show_and_tell 모델을 학습시키기 위한 코드입니다. <br><br>
**show_and_Tell_embedding.py** : 학습된 show_and_tell 모델에서 review와 image가 들어가있는 embedding을 추출하는 코드입니다. <br><br>
**tag_dataloader.py** : tag 모델에 적용시키기 위한 데이터 전처리 및 dataloader를 만드는 코드입니다.
<br><br>
**tag_mobilenet.py** : tag인 mobilenet 모델이 정의된 코드입니다.
<br><br>
**tag_train.py**: tag 모델을 학습시키기 위한 코드입니다.
<br><br>
**tag_embedding.py** : 학습된 tag 모델에서 tag와 image가 들어가 있는 embedding을 추출하는 코드입니다.
<br><br>
**similarity_result.py** : show and tell model의 embedding을과 tag model의 embedding을 결합하고, 투입된 image와 결합한 embedding 파일의 유사도를 구하여 가장 가까운 5개의 카페를 추천해주는 코드입니다.
<br>

## Results 
![Cafe-In 일단 완성 - 수정_37](https://user-images.githubusercontent.com/67720742/125879171-a50049e1-1e0a-4691-9d3b-653283caaa1d.png)

<br>

## Web Demo

[ 웹 데모](https://cafein-tobigs.netlify.app/)를 통해 직접 체험해보세요! <br><br>
이미지를 클릭하면 **Web Demo reposit**으로 연결됩니다.


<a href="https://github.com/YMGYM/tobigs_cafein_react_app" height="5" width="10" target="_blank">
	<img src="https://user-images.githubusercontent.com/67720742/125878431-c0f9dc87-94f7-41c4-aba2-5e393b1d521a.png" alt="위의 이미지를 누르면 연결됩니다.">
<a>


## Presentation
저희 프로젝트에 대해 자세하게 알고 싶으시다면, 프로젝트 설명자료를 참고해주세요. 
* [![GoogleDrive Badge](https://img.shields.io/badge/Presentation-405263?style=flat-square&logo=Quip&link=https://drive.google.com/file/d/1VnYsB8k4Fxu6UFhAxuTi4m01BjoH2uwS/view?usp=sharing)](https://drive.google.com/file/d/1BBPx9SF7cjF7q5UEAIsVVZp2RD5OEAl1/view?usp=sharing)
* [![Youtube Badge](https://img.shields.io/badge/Youtube-ff0000?style=flat-square&logo=youtube&link=https://youtu.be/KPS1sD_lcMc)](https://youtu.be/KPS1sD_lcMc)


## Contributors
빅데이터 동아리 **[ToBig's](http://www.datamarket.kr/xe/)** 멤버들이 함께한 프로젝트입니다.
<table>
  <tr>
    <td align="center"><a href="https://github.com/pjy970108"><img src="https://user-images.githubusercontent.com/67720742/125877128-50deb393-24ea-4ec0-a002-341f31f76156.jpg" width="150" height="150"><br /><sub><b>박준영</b></sub></td>
    <td align="center"><a href="https://github.com/jiwoo0212"><img src="https://user-images.githubusercontent.com/67720742/125877217-f8d4d731-e5a9-41f6-8820-5223a4d6b0c6.jpg" width="150" height="150"><br /><sub><b>강지우</b></sub></td>
    <td align="center"><a href="https://github.com/Yu-JIn22"><img src="https://user-images.githubusercontent.com/67720742/125877246-efaefdef-e61a-4e96-8aad-d38efa95b71e.jpg" width="150" height="150"><br /><sub><b>한유진</b></sub></td>
    <td align="center"><a href="https://github.com/YMGYM"><img src="https://user-images.githubusercontent.com/67720742/125877285-c0b3eac0-27c7-405d-85fb-2c5cf80e5c12.jpg" width="150" height="150"><br /><sub><b>안민준</b></sub></td>
  </tr>
</table>

<table>
  <tr>
    <td align="center"><a href="https://github.com/yoonj98"><img src="https://user-images.githubusercontent.com/67720742/125877317-9c91c97c-2916-4bd3-a20b-fdbe9b1dc498.jpg" width="150" height="150"><br /><sub><b>이윤정</b></sub></td>
    <td align="center"><a href="https://github.com/KimHyeon-Ji"><img src="https://user-images.githubusercontent.com/67720742/125877372-c051d315-4e93-47d1-81fb-02d0a4a2332c.jpg" width="150" height="150"><br /><sub><b>김현지</b></sub></td>
    <td align="center"><a href="https://github.com/jaeyoung-kang"><img src="https://user-images.githubusercontent.com/67720742/125877506-e74f752f-3842-47d0-ab18-13dfb6680dc2.png" width="150" height="150"><br /><sub><b>강재영</b></sub></td>
    <td align="center"><a href="https://github.com/stillpsy"><img src="https://user-images.githubusercontent.com/67720742/125895509-e2d0f432-b23f-498a-925a-46a52e9bbd2b.png" width="150" height="150"><br /><sub><b>이원도</b></sub></td>
