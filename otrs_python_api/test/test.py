import unittest

from otrs_python_api import article, otrs
import socutils

from otrs_python_api.ticket import Ticket
from otrs_python_api.utils.configuration_loading import prepare_logging


prepare_logging("INFO")


def tickets_close(otrs_client, ticket_ids):
    """ Перевод всех тестовых заявок за последние time_interval минут
        в закрытые.
    """
    for ticket_id in ticket_ids:
        ticket = otrs_client.ticket_get(ticket_id)
        ticket.set_field('ServiceID', None)
        ticket.set_field('Service', None)
        ticket.set_field('StateID', '2')
        ticket.set_field('SLAID', None)
        ticket.set_field('SLA', None)
        ticket.set_field('Priority', None)
        ticket.set_field('PriorityID', None)
        otrs_client.ticket_update(ticket_id, ticket)


class TestOTRS(unittest.TestCase):
    def setUp(self):
        self.otrs_client = otrs.OTRS(
            url=setting['OTRS']['url'],
            login=setting['OTRS']['login'],
            password=setting['OTRS']['password'],
            interface=setting['OTRS']['interface'],
            verify=setting['OTRS']['verify'],
            priority=setting['OTRS']['priority']
        )

        self.ticket_creation_data = socutils.get_settings(ticket_creation_data_filename)
        ticket = Ticket.create(
            Title=self.ticket_creation_data['Title'],
            StateID=self.ticket_creation_data['StateID'],
            PriorityID=self.ticket_creation_data['PriorityID'],
            CustomerUser=self.ticket_creation_data['CustomerUser'],
            TypeID=self.ticket_creation_data['TypeID'],
            ServiceID=self.ticket_creation_data['ServiceID'],
            QueueID=self.ticket_creation_data['QueueID'])
        created_ticket = self.otrs_client.ticket_create(ticket, article.Article(Subject="TestSubject", Body="Test",
                                                                                MimeType='text/plain'))
        self.ticket_id = created_ticket['TicketID']
        self.list_created_ticket = [self.ticket_id]

    def test_ticket_create(self):
        ticket = Ticket.create(
            Title=self.ticket_creation_data['Title'],
            StateID=self.ticket_creation_data['StateID'],
            PriorityID=self.ticket_creation_data['PriorityID'],
            CustomerUser=self.ticket_creation_data['CustomerUser'],
            TypeID=self.ticket_creation_data['TypeID'],
            ServiceID=self.ticket_creation_data['ServiceID'],
            QueueID=self.ticket_creation_data['QueueID'])
        with open(article_body_filename, 'r') as f:
            body = f.read()
        ticket_article = article.Article(Subject="TestSubject", Body=body, MimeType='text/html')
        ticket.set_dynamic_field('TicketIPAddress', self.ticket_creation_data['dynamic_field']['TicketIPAddress'])
        ticket.set_dynamic_field('TicketComputerName', self.ticket_creation_data['dynamic_field']['TicketComputerName'])
        ticket.set_dynamic_field('device', self.ticket_creation_data['dynamic_field']['device'])
        created_ticket = self.otrs_client.ticket_create(ticket, ticket_article)
        ticket_id = created_ticket['TicketID']
        self.list_created_ticket.append(ticket_id)
        ticket_ids = self.otrs_client.ticket_search(TicketID=ticket_id)
        self.assertFalse(not ticket_ids)
        self.assertEqual(ticket_id, ticket_ids[0])

    def tearDown(self):
        tickets_close(self.otrs_client, self.list_created_ticket)


if __name__ == '__main__':
    unittest.main()
