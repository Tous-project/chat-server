# 공통 사항:
    - 로그인하지 않았을때: 403, Forbidden
    - 입력 데이터가 잘못됐을때: 400, InvalidParameter
    - 세션이 유효하지 않을때: 401, Unauthorized


## 채팅방 생성

- method: POST
- url: /rooms
- cookie:
    - session
- body:
    - name
- response:
    - 정상: 201
        - body:
            - room_id
              name
              owner
    - 이미 채팅방이 있을때: 400, AlreadyExist
        - body:
            - error_message
    - 입력 데이터가 잘못됐을때: 400, InvalidParameter
        - body:
            - error_message


## 채팅방 리스트

- method: GET
- url: /rooms
- cookie:
    - session
- response:
    - 정상: 200 (없으면 빈배열)
        - body:
            - room_id
              name
              owner


## 채팅방 삭제

- method: DELETE
- url: /rooms/{room_id}
- cookie:
    - session
- response:
    - 정상: 204
        - body: null
    - 입력 데이터가 잘못됐을때: 400, InvalidParameter
        - body:
            - error_message
    - 내가 채팅방 주인이 아닐때: 401, Unauthorized
        - body:
            - error_message



## 채팅방 입장

- method: ws
- url: /rooms/{room_id}

### 최초 입장, 이미 들어온적 있음
유저 목록에 있는 유저인지로 판단


### 채팅방 나갈때(버튼을 눌러서 진짜 나감)
socket으로 보내는 메시지 action으로 판단
leave: 채팅방 유저 목록에서 제거
WebSocketDisconnect: 아무것도 안함



## 유저 생성

- method: POST
- url: /users
- body:
    - user_id
    - password
    - email
    - name
- response:
    - 정상: 201
        - body:
            - id
            - user_id
            - password
            - email
            - name
    - 이미 존재하는 아이디: 400
        - body:
            - error_message


## 유저 삭제

- method: DELETE
- url: /users/me
- cookie:
    - session
- response:
    - 정상: 204
        - body: null


## 유저 조회
- method: GET
- url: /users/me
- cookie:
    - session
- response:
    - 정상: 200
        - body:
            - id
            - user_id
            - password
            - email
            - name


## 유저 로그인
- method: POST
- url: /login
- body:
    - user_id
    - password
- response:
    - 정상: 205
        - body:
            - session
    - 정보가 틀림(id or password): 404
        - body:
            - error_message


## 유저 로그아웃
- method: DELETE
- url: /logout
- cookie:
    - session
- response:
    - 정상: 204
        - body: null



--------

유저
id
name
user_id
password
email


채팅방
id
room_id
name
owner



세션
id
session_id
user_id
device
