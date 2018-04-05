from django.db import models

__all__ = (
    'Reservation',
)


class Reservation(models.Model):

    check_in = models.DateField(unique=True)
    check_out = models.DateField(unique=True)
    guest_num = models.PositiveSmallIntegerField(blank=True, default=1)
    bank_account = models.CharField(max_length=30)

    house = models.ForeignKey(
        'House',
        on_delete=models.SET_NULL,
    )

    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)

    # PAYMENT_TYPE_DEPOSIT = 'DE'
    # PAYMENT_TYPE_CREDITCARD = 'CR'
    # PAYMENT_TYPE_PAYPAL = 'PA'
    #
    # PAYMENT_TYPE_CHOICES = (
    #     (PAYMENT_TYPE_DEPOSIT, '무통장입금'),
    #     (PAYMENT_TYPE_CREDITCARD, '신용카드'),
    #     (PAYMENT_TYPE_PAYPAL, '페이팔')
    # )
    # payment_type = models.CharField(choices=PAYMENT_TYPE_CHOICES, default=)


    # message 구현여부에 따라 결정
    # message_to_host = models.TextField(max_length=300)

    def __str__(self):
        return f'Host: {self.house.name} Guest: {self.user.username}'
