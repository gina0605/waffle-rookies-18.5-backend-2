# waffle-rookies-18.5-backend-2

## Grace Day
학교 시험 준비 등으로 바빠서 Grace Day 하루 사용하겠습니다. (10/12 월요일까지)

## test를 통해 고친 부분
- `POST /api/v1/user/`
  * Participant의 경우, `accepted`가 입력으로 주어지지 않을 시 default로 True로 설정하도록 바꿈. 
  * 새로운 instructor를 만들 때 런타임 에러가 남. 코딩 실수를 고침.
- `POST /api/v1/user/participant/`
  * `accepted`가 입력으로 주어지지 않을 시 default로 True로 설정하도록 바꿈.
- `DELETE /api/v1/seminar/{seminar_id}/user/`
  * 이미 드랍한 유저의 경우, 200OK로 응답하는 것이 더 합당하다 생각하고 바꿈.
