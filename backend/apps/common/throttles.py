from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AgroNovaAnonRateThrottle(AnonRateThrottle):
    scope = 'anon'


class AgroNovaUserRateThrottle(UserRateThrottle):
    scope = 'user'
