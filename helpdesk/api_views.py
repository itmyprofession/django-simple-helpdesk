from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination

from helpdesk.models import Ticket, State, Assignee
from helpdesk.serializers import TicketListSerializer, StateSerializer, AssigneeSerializer, TicketDetailSerializer


class Pagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'limit'


class TicketListView(ListAPIView):
    serializer_class = TicketListSerializer
    pagination_class = Pagination

    def get_queryset(self):
        filters = {}
        state = self.request.query_params.get('state', '')
        if state:
            filters['state'] = state

        if not self.request.user.has_perm('helpdesk.view_all_tickets'):
            filters['assignee'] = self.request.user
        else:
            assignee = self.request.query_params.get('assignee', '')
            if assignee == 'me':
                filters['assignee'] = self.request.user
            elif assignee:
                filters['assignee__pk'] = int(assignee)

        search = self.request.query_params.get('search', '')
        qs = Q()
        if search:
            qs |= Q(title__icontains=search) | Q(body__icontains=search)
            if self.request.user.has_perm('helpdesk.view_all_tickets'):
                qs |= Q(customer__icontains=search)
        return Ticket.objects.filter(qs, **filters)


class TicketView(RetrieveUpdateAPIView):
    serializer_class = TicketDetailSerializer

    def get_queryset(self):
        filters = {}
        if not self.request.user.has_perm('helpdesk.view_all_tickets'):
            filters['assignee'] = self.request.user

        return Ticket.objects.filter(**filters)


class StateListView(ListAPIView):
    serializer_class = StateSerializer
    queryset = State.objects.all()


class AssigneeListView(ListAPIView):
    serializer_class = AssigneeSerializer
    queryset = Assignee.objects.all()
