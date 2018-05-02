from django.core.paginator import Paginator


class CustomPagination():
    DEFAULT_PAGE_SIZE = 25
    MAX_PAGE_SIZE = 50

    def __init__(self, users, request):
        self.users = users
        self.page = request.GET.get('page', 1)
        self.page_size = min(
            int(request.GET.get('page_size', self.DEFAULT_PAGE_SIZE)),
            self.MAX_PAGE_SIZE
        )

    @property
    def object_list(self):
        paginator = Paginator(self.users, self.page_size)

        return paginator.get_page(self.page).object_list

    # Page number까지 표현해주려고 만들어둔 method
    # @property
    # def get_page(self):
    #     return self.page
