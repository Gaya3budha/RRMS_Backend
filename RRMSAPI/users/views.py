from django.forms import ValidationError
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny

from caseInfoFiles.models import Notification
from users.utils import generate_otp, send_otp_email, send_password_reset_email, send_password_setup_email
from .serializers import PasswordResetRequestSerializer, UserSerializer, CustomTokenObtainPairSerializer, UserSearchSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import PasswordResetOTP, PasswordResetRequest, User, ActiveUser, Designation
from mdm.models import Role
from mdm.permissions import IsSuperAdminOrReadOnly
from datetime import date
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode


# Create your views here.
class UserListView(APIView):
    def get(self,request,*args,**kwargs):
        user = request.user
        
        if user.is_superuser:
            users=User.objects.all()
        
        serializer = UserSerializer(users, many= True, context={'request': request})
        return Response(serializer.data,status = status.HTTP_200_OK)

class CreateUserView(APIView):
    permission_classes = [IsSuperAdminOrReadOnly]
    def post(self,request,*args,**kwargs):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(serializer.data,status = status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

        return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class SetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not all([uid, token, new_password]):
            return Response({"error": "Missing data."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid)
            print('user',user.email)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid UID."}, status=status.HTTP_400_BAD_REQUEST)

        print("Expected token:", default_token_generator.make_token(user))
        print("Received token:", token)

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.is_passwordset = True
            user.save()
            return Response({"success": "Password has been set for the user."})
        else:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

class RequestPasswordResetOTP(APIView):
    def post(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            user = User.objects.get(kgid=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        otp = generate_otp()
        PasswordResetOTP.objects.create(user=user, otp=otp)
        print('email', user.email)
        send_otp_email(user.email, otp)
        # send_otp_sms(user.mobileno, otp)

        return Response({'message': 'OTP sent to registered email.'})

class VerifyPasswordResetOTP(APIView):
    def post(self, request):
        user_id = request.data.get('kgid')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(kgid=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Invalid user ID'}, status=404)

        try:
            otp_entry = PasswordResetOTP.objects.filter(user=user, otp=otp, is_used=False).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            return Response({'error': 'Invalid or used OTP'}, status=400)

        if otp_entry.is_expired():
            return Response({'error': 'OTP has expired'}, status=400)

        otp_entry.is_used = True
        otp_entry.save()

        return Response({'message': 'OTP validated. You can now reset the password.'})

class ResetPassword(APIView):
    def post(self, request):
        user_id = request.data.get('kgid')
        new_password = request.data.get('password')

        try:
            user = User.objects.get(kgid=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Invalid user ID'}, status=404)

        user.set_password(new_password)
        user.is_passwordset = True
        user.save()

        return Response({'message': 'Password reset successful.'})
class UpdateUserView(APIView):
    def patch(self,request,kgid_user,*args,**kwargs):
        try:
            # getting the user based on kgid
            user = User.objects.get(kgid = kgid_user)
            data = request.data

            original_role_id = user.role.roleId if user.role else None
            original_active = user.is_active

            new_role_id = int(data.get('roleId', original_role_id)) if data.get('roleId') else original_role_id
            new_is_active = data.get('isActive', original_active)

            print("new_role_id",new_role_id)
            print("new_is_active",new_is_active)

            ADMIN_ROLE_ID = 1

            becoming_active_admin = (
                new_role_id == ADMIN_ROLE_ID and new_is_active and
                (original_role_id != ADMIN_ROLE_ID or not original_active)
            )

            print("becoming_active_admin",becoming_active_admin)

            if becoming_active_admin:
                active_admin_count = User.objects.filter(
                    role__roleId=ADMIN_ROLE_ID,
                    is_active=True
                ).exclude(pk=user.pk).count()

                if active_admin_count >= 5:
                    return Response(
                        {"error": "Cannot have more than 5 active Admin users."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
           

           
            if 'roleId' in data:
                try:
                    new_role = Role.objects.get(roleId=data['roleId'])
                    user.role = new_role
                except Role.DoesNotExist:
                    return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

            # Handle designation update (many-to-many)
            if 'designationIds' in data:
                designation_ids = data['designationIds']

                if isinstance(designation_ids, list):
                    designations = Designation.objects.filter(designationId__in=designation_ids)
                    if designations.count() != len(designation_ids):
                        return Response({"error": "One or more designation IDs are invalid"}, status=status.HTTP_400_BAD_REQUEST)
                    user.designation.set(designations)
                else:
                    return Response({"error": "designationIds must be a list"}, status=status.HTTP_400_BAD_REQUEST)
                
            if 'password' in data:
                user.set_password(data['password'])
            
            if 'isActive' in data:
                user.is_active = data['isActive']
            
           
            excluded = ['id', 'password', 'role', 'designation', 'roleId', 'designationIds', 'is_active']
            updatable_fields = [field.name for field in User._meta.fields if field.name not in excluded]

            # Apply any other updates (currently only role is handled via updated_data)
            for key, value in data.items():
                if key in updatable_fields:
                    setattr(user, key, value)


            user.save()

            serializer = UserSerializer(user,  context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self,request):
        serializer_class = CustomTokenObtainPairSerializer(data = request.data)

        try:
            serializer_class.is_valid(raise_exception=True)
        except AuthenticationFailed as e:
            return Response({
                "responseData": str(e),
                "statusCode": 401
            }, status=status.HTTP_401_UNAUTHORIZED)
        user = serializer_class.user
        password_set = serializer_class.validated_data.pop("passwordSet", False)

        if not password_set:
            # Password is not set → skip token generation
            return Response({
                "passwordSet": False,
                "responseData": {},
                "statusCode": 200
            }, status=status.HTTP_200_OK)
        ActiveUser.objects.update_or_create(user=user)
        return Response({"passwordSet": True,"responseData": serializer_class.validated_data, "statusCode": 200},
                         status=status.HTTP_200_OK)



class GetLoggedInUsersView(APIView):
    #  permission_classes = [IsAdminUser]
     
     def get(self, request, *args, **kwargs):
        active_users = ActiveUser.objects.select_related('user').filter(last_login__date=date.today())

        print('active_users',active_users)
        active_users_data = UserSerializer([a.user for a in active_users], many=True, context={'request': request})


        return Response({
            "count": active_users.count(),
            "users": active_users_data.data
        })

class GetDivisionrAdminsView(APIView):
    def post(self, request):
        divsion_id =request.data.get("division_id")
        role_id =request.data.get("role_id")

        print("role_id",role_id)
        print("division_id",divsion_id)

        users = User.objects.filter(role__roleId=3,designation__division__divisionId=divsion_id,is_active=True)

        print("users",users)
        serialized_users = UserSerializer(users, many=True)

        return Response({
            "users" : serialized_users.data
        })


class SearchUsersAPIView(APIView):
    def post(self, request):
        searchParams = request.data
        query = Q()
        filters_applied = False

        if "departmentId" in searchParams and searchParams["departmentId"] not in [None, ""]:
            query &= Q(designation__department__departmentId__icontains = searchParams['departmentId'])
            filters_applied = True

        if "divisionId" in searchParams and searchParams["divisionId"] not in [None, ""]:
            query &= Q(designation__division__divisionId__icontains= searchParams['divisionId'])
            filters_applied = True

        if "designationId" in searchParams and searchParams["designationId"] not in [None, ""]:
            query &= Q(designation__designationId__icontains= searchParams['designationId'])
            filters_applied = True
        
        if "firstName" in searchParams and searchParams["firstName"] not in [None, ""]:
            query &= Q(first_name__icontains= searchParams['firstName'])
            filters_applied = True

        if "lastName" in searchParams and searchParams["lastName"] not in [None, ""]:
            query &= Q(last_name__icontains= searchParams['lastName'])
            filters_applied = True

        if "mobileNo" in searchParams and searchParams["mobileNo"] not in [None, ""]:
            query &= Q(mobileno__icontains= searchParams['mobileNo'])
            filters_applied = True
        
        if "kgid" in searchParams and searchParams["kgid"] not in [None, ""]:
            query &= Q(kgid__icontains= searchParams['kgid'])
            filters_applied = True

        if filters_applied:
            queryset = User.objects.filter(query).prefetch_related('designation__division','designation__department').distinct()
        else:
            queryset = User.objects.all()

        serializer = UserSearchSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RequestPasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data

            kgid = validated_data.get('kgid')
            try:
                user = User.objects.get(kgid=kgid)
            except User.DoesNotExist:
                return Response({'error': 'User with this KGID does not exist.'}, status=status.HTTP_404_NOT_FOUND)

            # Create the password reset request
            reset_request = PasswordResetRequest.objects.create(
                kgid=kgid,
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                email=validated_data.get('email'),
                mobileno=validated_data.get('mobileno'),
                requested_by=user
            )

            return Response({'message': 'Request received by admin. You shall be notified shortly.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ViewDatafromNotificationPasswordRequest(APIView):
    def get(self, request, pk, *args, **kwargs):
        try:
            Notification.objects.filter(object_id=pk).update(is_read=True)

            pwdRequestData=PasswordResetRequest.objects.get(passwordResetRequestId=pk)
            print(pwdRequestData)
            user= pwdRequestData.requested_by

           
            return Response({
                'email': user.email,
                'mobileNo':user.mobileno,
                'userName': user.first_name+' '+user.last_name,
                'pwdRequestEmail':pwdRequestData.email,
                'pwdResetRequestId':pwdRequestData.passwordResetRequestId,
                'pwdRequestMobileNo':pwdRequestData.mobileno,
                'kgid':user.kgid
            }, status=200)
        except PasswordResetRequest.DoesNotExist:
            return Response({'message':'Password Request doesnt exists'},status=404)
        except User.DoesNotExist:
            return Response({'message':f'user with kgid doesnt exists'},status=404)

class SetDefaultPwd(APIView):
    def post(self,request,pk,*args,**kwargs):
        existingUser=User.objects.get(kgid=pk)
        existingUser.set_password(request.data.get("defaultPwd"))
        existingUser.is_passwordset=False
        existingUser.save(update_fields=['password','is_passwordset'])
        return Response({'message':'Default Password set for the user successfully'},status=200)
    
class PasswordResetRequestListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        requests = PasswordResetRequest.objects.all().order_by('-requested_at') 
        serializer = PasswordResetRequestSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class SetStatusForUser(APIView):
    def post(self,request,*args,**kwargs):
        pwdRequestData=PasswordResetRequest.objects.get(passwordResetRequestId=request.data.get("pwdId"))
        
        status_value = request.data.get("status")

        if status_value not in ["approved", "rejected"]:
            return Response({"message": "Invalid status. Must be 'approved' or 'rejected'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Update status
        pwdRequestData.status = status_value
        pwdRequestData.save(update_fields=['status'])

        if status_value == "approved":
            # You can also return the tokenized set password URL if needed
            frontend_url = f"https://rrms-frontend.vercel.app/manage-user/reset-password"
            return Response({
                "message": "Request approved. Redirect to reset password screen.",
                "redirect_url": frontend_url
            }, status=status.HTTP_200_OK)

        return Response({"message": "Request has been rejected."}, status=status.HTTP_200_OK)

class SendPasswordResetLink(APIView):
    def post(self,request,pk,*args,**kwargs):
        pwdRequestData=PasswordResetRequest.objects.get(passwordResetRequestId=pk)

        given_user=pwdRequestData.requested_by

        given_user.is_passwordset=False
        given_user.save(update_fields=['is_passwordset'])

        # given_user.email=pwdRequestData.email
        # given_user.mobileno=pwdRequestData.mobileno

        send_password_reset_email(user=given_user,to_email=pwdRequestData.email)

        return Response({'message':'Password Reset Link Sent Successfully'},status=200)
    
class SetPwdAfterReset(APIView):
    def post(self,request,pk,*args,**kwargs):
        existingUser=User.objects.get(kgid=pk)
        existingUser.set_password(request.data.get("password"))
        existingUser.is_passwordset=False
        existingUser.save(update_fields=['password','is_passwordset'])
        return Response({'message':'Password set for the user successfully'},status=200)
    
