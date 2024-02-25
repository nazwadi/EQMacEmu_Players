from django.db import models
from django.utils import timezone


# Create your models here.
class LoginServerAccounts(models.Model):
    """
    This model should be tied to the database specified in the LoginServerRouter
    """

    def __str__(self):
        return self.AccountName

    LoginServerID = models.AutoField(primary_key=True, null=False)
    AccountName = models.CharField(max_length=30, null=False, unique=True)
    AccountPassword = models.CharField(max_length=50, null=False)
    AccountCreateDate = models.DateTimeField(auto_created=True, null=False, default=timezone.now)
    AccountEmail = models.EmailField(max_length=100, null=False)
    LastLoginDate = models.DateField(null=False, default=timezone.now)
    LastIPAddress = models.GenericIPAddressField(max_length=15, null=False)
    created_by = models.IntegerField(null=False, default=0)
    client_unlock = models.SmallIntegerField(null=False)
    creationIP = models.GenericIPAddressField(max_length=15, null=False)
    ForumName = models.CharField(max_length=30, null=False)
    max_accts = models.SmallIntegerField()
    Num_IP_Bypass = models.SmallIntegerField(null=True)
    lastpass_change = models.BigIntegerField(null=True)

    class Meta:
        db_table = "tblLoginServerAccounts"
        verbose_name_plural = "Login Server Accounts"


class ServerAdminRegistration(models.Model):
    """
    This model should be tied to the database specified in the LoginServerRouter
    """

    def __str__(self):
        return str(self.ServerAdminID) + " - " + self.AccountName + " - " + self.Email

    ServerAdminID = models.AutoField(primary_key=True, null=False)
    AccountName = models.CharField(max_length=30, null=False)
    AccountPassword = models.CharField(max_length=30, null=False)
    FirstName = models.CharField(max_length=40, null=False)
    LastName = models.CharField(max_length=50, null=False)
    Email = models.EmailField(max_length=100, null=False)
    RegistrationDate = models.DateTimeField(null=False)
    RegistrationIPAddr = models.GenericIPAddressField(max_length=15, null=False)

    class Meta:
        db_table = "tblServerAdminRegistration"
        verbose_name_plural = "Server Admin Registrations"


class ServerListType(models.Model):
    """
    This model should be tied to the database specified in the LoginServerRouter
    """

    def __str__(self):
        return str(self.ServerListTypeID) + " - " + self.ServerListTypeDescription

    ServerListTypeID = models.IntegerField(primary_key=True, null=False)
    ServerListTypeDescription = models.CharField(max_length=20, null=False)

    class Meta:
        db_table = "tblServerListType"
        verbose_name_plural = "Server List Types"


class WorldServerRegistration(models.Model):
    """
    This model should be tied to the database specified in the LoginServerRouter
    """

    def __str__(self):
        return str(self.ServerID) + " - " + str(self.ServerLongName) + " - " + str(self.ServerTagDescription)

    ServerID = models.AutoField(primary_key=True, null=False)
    ServerLongName = models.CharField(max_length=100, null=False)
    ServerTagDescription = models.CharField(max_length=50, null=False)
    ServerShortName = models.CharField(max_length=25, null=False)
    ServerListTypeID = models.IntegerField(null=False, default=3)
    ServerLastLoginDate = models.DateField(null=True)
    ServerLastIPAddr = models.GenericIPAddressField(null=True)
    ServerAdminID = models.IntegerField(null=False)
    ServerTrusted = models.IntegerField(null=False)
    Note = models.CharField(max_length=300, null=True)

    class Meta:
        db_table = "tblWorldServerRegistration"
        verbose_name_plural = "World Server Registrations"


class Account(models.Model):
    """
    This model is tied to the GameServerRouter.  It allows us to
    tie a character at char select to a login server account and forum account.
    """

    def __str__(self):
        return str(self.name) + " " + str(self.charname)

    id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=30, unique=True, null=False)
    charname = models.CharField(max_length=64, null=False)
    sharedplat = models.IntegerField(default=0, null=False)
    password = models.CharField(max_length=50, null=False)
    status = models.IntegerField(default=0, null=False)
    lsaccount_id = models.IntegerField(default=None, unique=True, null=False)
    forum_id = models.IntegerField(default=0, null=False)
    gmspeed = models.SmallIntegerField(default=0, null=False)
    revoked = models.SmallIntegerField(default=0, null=False)
    karma = models.IntegerField(default=0, null=False)
    minilogin_ip = models.CharField(max_length=32, null=False)
    hideme = models.SmallIntegerField(default=0, null=False)
    rulesflag = models.SmallIntegerField(default=0, null=False)
    suspendeduntil = models.DateTimeField(default='0000-00-00 00:00:00', null=False)
    time_creation = models.IntegerField(default=0, null=False)
    expansion = models.SmallIntegerField(default=12, null=False)
    ban_reason = models.TextField(default=None, null=True)
    suspend_reason = models.TextField(default=None, null=True)
    active = models.SmallIntegerField(default=0, null=False)
    ip_exemption_multiplier = models.IntegerField(default=1, null=True)
    gminvul = models.SmallIntegerField(default=0, null=False)
    flymode = models.SmallIntegerField(default=0, null=False)
    ignore_tells = models.SmallIntegerField(default=0, null=False)
    mule = models.SmallIntegerField(default=0, null=False)

    class Meta:
        db_table = "account"

