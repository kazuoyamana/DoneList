from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(UserManager):
    """カスタムユーザーマネージャー"""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    カスタムユーザーモデル
    username の代わりに email で識別。ユーザー名は表示用なので日本語OK。
    ここでは基本的によくアクセスされる項目を追加する。
    それ以外はProfileなどの One to One で紐付けたモデルに追加する。
    """

    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(
        _('username'), max_length=50, blank=True,
        help_text='ホーム画面などで表示される名前です（日本語も使えます）',
    )
    avatar = models.ImageField('プロフィール画像', upload_to='uploads', null=True, blank=True)
    # カレンダーの週始まり設定。Trueで日曜始まりになる
    week_status = models.BooleanField('週の始まりを日曜にする（デフォルトは月曜）', default=False)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'       # メールのフィールド名を指定
    USERNAME_FIELD = 'email'    # ユニークなフィールドを指定

    # createsuperuserで入力を求められるフィールド名のリスト
    # 普通のUserでは username / password は自動で含まれる
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Profile(models.Model):
    """
    UserモデルをOneToOneで拡張したプロフィール
    ここにはあまりアクセスのない項目を追加する
    """
    bio = models.TextField('自己紹介', max_length=1000, blank=True)
    website = models.URLField('URL', max_length=500, help_text='ホームページURLを入力してください', blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'profile'

    def __str__(self):
        # userオブジェクトをそのまま渡すとエラーになるのでstrにする
        return str(self.user)

