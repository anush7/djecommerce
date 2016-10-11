import braintree
import os
import uuid

from django.conf import settings
from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Permission, Group
from django.utils.translation import ugettext_lazy as _


if settings.DEBUG:
    braintree.Configuration.configure(braintree.Environment.Sandbox,
      merchant_id=settings.BRAINTREE_MERCHANT_ID,
      public_key=settings.BRAINTREE_PUBLIC,
      private_key=settings.BRAINTREE_PRIVATE)

def generate_uuid():
    return str(uuid.uuid4()).replace("-", "")

class EGroup(Group):
    categories = models.ManyToManyField('catalog.CatalogCategory',blank=True)
    is_import = models.BooleanField(default=False)
    is_export = models.BooleanField(default=False)

    def check_permission(model_permission):
        permission = Permission.objects.get(codename=model_permission)
        if permission in self.permissions.all():return True
        else:return False

class EcUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, is_staff, is_superuser, first_name, last_name):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,username=username,
                          first_name=first_name, last_name=last_name,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          date_joined=now)
        user.uuid = generate_uuid()
        user.uniqueid = user.uuid[:4]
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, first_name=None, last_name=None):
        return self._create_user(username, email, password, False, False, first_name, last_name)

    def create_superuser(self, username, email, password, first_name=None, last_name=None):
        return self._create_user(username, email, password, True, True, first_name, last_name)



class EcUser(AbstractBaseUser, PermissionsMixin):
    username    = models.CharField(max_length=254, unique=True)
    first_name  = models.CharField(max_length=254, blank=True)
    last_name   = models.CharField(max_length=254, null=True, blank=True)
    email       = models.EmailField(blank=True, unique=True)
    is_admin    = models.BooleanField(default=False)
    is_staff    = models.BooleanField(default=False)
    is_partner  = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    address1    = models.CharField(max_length=254, null=True, blank=True)
    address2    = models.CharField(max_length=254, null=True, blank=True)
    area_code   = models.CharField(max_length=20, null=True, blank=True)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    uuid        = models.CharField(max_length=75, null=True, blank=True)
    uniqueid    = models.CharField(max_length=75, null=True, blank=True)
    braintree_id = models.CharField(max_length=120, null=True, blank=True)

    objects = EcUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    class Meta:
        verbose_name = _('EcUser')
        verbose_name_plural = _('ecusers')
        
    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_roles(self):
        return self.groups.values_list('id',flat=True)

    @property
    def get_braintree_id(self):
        instance = self
        if not instance.braintree_id:
            result = braintree.Customer.create({
                "email": instance.email,
            })
            if result.is_success:
                instance.braintree_id = result.customer.id
                instance.save()
        return instance.braintree_id

    def get_client_token(self):
        customer_id = self.get_braintree_id
        if customer_id:
            client_token = braintree.ClientToken.generate({
                "customer_id": customer_id
            })
            return client_token
        return None
