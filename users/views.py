import requests, jwt

from django.views       import View
from django.http        import JsonResponse

from starfolio.settings import SECRET_KEY, ALGORITHM
from users.models       import User

class KakaoLogInView(View):
    def get(self, request):
        try:
            kakao_access_token  = request.headers.get('Authorization')           
            kakao_user_info_api = 'https://kapi.kakao.com/v2/user/me'
            user_info_response  = requests.get(kakao_user_info_api, headers={'Authorization' : f'Bearer {kakao_access_token}'}, timeout=2).json()

            if user_info_response.get('code') == -401:
                return JsonResponse({'message' : 'INVALID_TOKEN'}, status = 401)

            kakao_id = user_info_response['id']
            name     = user_info_response['properties']['nickname']
            email    = user_info_response['kakao_account']['email']
            
            user, is_created = User.objects.get_or_create(
                    kakao_id = kakao_id,
                    defaults={'name' : name, 'email' : email}
            )
            
            data = {
                'access_token' : jwt.encode({'id' : user.id}, SECRET_KEY, ALGORITHM),
                'name'         : name,
                'email'        : email
            }
            
            return JsonResponse({'message' : 'SUCCESS', 'data' : data}, status = 200)
        
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)