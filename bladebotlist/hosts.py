from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(r"www", "main_site.urls", name="www"),
    host(r"admin", "bladebotlist.urls", name="admin"),
    host(r"api", "api.urls", name="api"),
)
