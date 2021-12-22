# 카페-인 웹 데모 백엔드 서버

## 개요
카페인 웹 데모 백엔드 서버 코드입니다. `Django` 로 작성되었습니다.

서비스를 실행시키기 위해서 다음 명령어를 실행하세요

`python3 manage.py runserver`

## 디렉토리

프로젝트는 다음 디렉토리로 이루어져 있습니다.
- `main` : 기본 API를 담당하는 앱입니다.
    - `main/model` : 카페-인 모델이 저장되어 있습니다.
    - `main/views.py` : 모델 추론 코드가 저장되어 있습니다.
- `tobigs_cafeIn` : 설정 페이지입니다.


## API 코드
프로젝트는 다음 API 통신을 지원합니다.

|url|method|description|parameter|return|
|:---:|:---:|:---:|:---:|:---:|
|`main/status`|`GET`|API 상태 체크|없음|`{"status":"OK"}`|
|`main/result`|`POST`|모델 추론|`{"img":<업로드된 파일>}`|`{"value":<모델 추론 결과>}`|
|`main/getImg`|`GET`|아이디에 해당되는 카페 이미지 반환|`{"imgId": <이미지 파일 이름>}`|이미지 파일|


오류 코드는 생략합니다.