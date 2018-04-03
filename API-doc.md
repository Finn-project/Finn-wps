#  API 사용법
### 박수민, 송영기
#### Version : v01
--




## User list
* URL : /user/
* Request : GET

> 정상 Response : 유저 리스트 JSON 반환





## User 정보 한개만 조회
* URL : /user/{PK}/
* Request : GET

> 정상 Response : 개별 유저정보 JSON 반환





## User signup
* URL : /user/
* Request : POST
* Body
	* email - 아이디 대신 이메일 주소 사용 (필수)
	* password1 - 비밀번호 (필수)
	* password2 - 확인용 비밀번호(password1과 동일한 값) (필수)
	* first_name - (선택), text
	* last_name - (선택), text
	* birthday - (선택), 날짜형식, 기본값: 1990-01-01
	* agreement - (선택), Boolean, 기본값: True

> 정상 Response : 가입을 시도한 email 반환








## User login
* URL : /user/login/
* Request : POST
* Body
	* email - 가입한 이메일 (필수)
	* password - 비밀번호 (필수)

> 정상 Response : User Token 및 User 정보 반환


## User logout
* URL : /user/logout/
* Request : POST
* Headers
	* Authorization : Token 67b53cd02~~~~ (필수)
	* email - 가입한 이메일 (필수)
	* password - 비밀번호 (필수)

> 정상 Response : "Logout Completed" (해더의 토큰이 서버에서 삭제됨)





## User 정보 수정
* URL : /user/{PK}/
* Request : PATCH
* Headers
	* Authorization : Token 67b53cd02~~~~ (필수)
* Body (아래 항목을 자유롭게 사용 가능)
	* img_profile - 프로필 이미지 (한장만 가능), 이미지 파일
	* gender - 성별, OTHER(기본값, 기타성별)/MALE(남자)/FEMALE(여자) 중 택1, 영어로 입력해야하고 대소문자 구분해서 입력해야 함, 위 3가지 단어중 한가지만 입력
	* birthday - 생일, 날짜형식만 입력 가능(기본값:1990-01-01)
	* phone_num - 연락처, text 20자 제한
	* preference_language - 선호 언어, text 20자 제한
	* preference_currency - 선호 통화, text 20자 제한
	* living_site - 거주지, text 100자 제한
	* introduce - 자기소개, text 300자 제한

> 정상 Response : 수정 시도한 User의 JSON 반환





## User 회원탈퇴(User 삭제)
* URL : /user/{PK}/
* Request : DELETE
* Headers
	* Authorization : Token 67b53cd02~~~~ (필수)
	* email - 가입한 이메일 (필수)
	* password - 비밀번호 (필수)

> 정상 Response : 아무것도 오지 않음, status 확인 > status 204 No Content 보이면 정상

<br>

---