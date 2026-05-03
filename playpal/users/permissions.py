from rest_framework import permissions

## created custom permission class
class IsUserOrReadOnly(permissions.BasePermission):
    ## custom users can only edit their own profile
    
    def has_permission(self, request, view):
        ## For list/create endpoints — only authenticated users can proceed
        if request.method in permissions.SAFE_METHODS:
            return True
        ## Write methods require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        ## Allow safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        ## Only the user can edit their own profile
        return obj == request.user 

## created custom permission class
class IsKidOwnerOrReadOnly(permissions.BasePermission):
    ## users can only edit their own kids profile
    
    def has_permission(self, request, view):
        ## For list/create endpoints — only authenticated users can proceed
        if request.method in permissions.SAFE_METHODS:
            return True
        ## Write methods require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        ## Allow safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        ## Only allow edit if user_id matches logged-in user (i.e the kids' profiles can only be edited by the parent)
        return obj.user_id == request.user
    
