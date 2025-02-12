from django.db import models

from userManagement.models import SalesPerson

class socialMediaRefCode(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    redirect = models.URLField()

    def __str__(self) -> str:return self.name

class contactInfo(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=14)
    email = models.EmailField()
    location = models.CharField(max_length=100)
    university = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField(null=True, blank=True)

    assigned_sales_person = models.ForeignKey(SalesPerson, on_delete=models.DO_NOTHING, related_name='contacts', blank=True, null=True)

    status = models.CharField(max_length=1, choices=(
        ('0','Not Contacted'),
        ('1','Not Answered'),
        ('2','Follow Up'),
        ('3','Not Interested'),
        ('4','Converted')
    ), default='0')
    follow_up_date = models.DateTimeField(blank=True, null=True)

    conversation_record = models.TextField(null=True, blank=True)

    ref = models.ForeignKey(socialMediaRefCode, on_delete=models.DO_NOTHING, related_name='contacts', blank=True, null=True)
    assigned_date = models.DateField(blank=True, null=True, editable=False)
    def __str__(self) -> str:return self.name

    # TODO: assigned date should be updated if it is itself null and assigned_sales_person is being chenged
    # def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:
    #     if self.name and self.assigned_sales_person and not self.assigned_date:self.assigned_date = timezone.now()
    #     return super().save(force_insert, force_update, using, update_fields)

    