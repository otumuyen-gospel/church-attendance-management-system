from .models import Role


def requiredGroups(permission):
    roles = Role.objects.filter(permissions__icontains=permission)
    groups = ['admin']
    for role in roles:
        if role.name.lower() != 'admin': #admin already added
          groups.append(role.name)
    
    return groups