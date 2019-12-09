from django.core.mail import send_mail

from dadabeauty.celery import app

@app.task
def send_active_email(email,url):
    def send_active_mail(email, code_url):
        subject = '达达商城用户激活邮件'
        html_message = '''
        <p>尊敬的用户 您好</p>
        <p>激活地址为<a href='%s' target='blank'>点击激活</a></p>
        ''' % (code_url)
        send_mail(subject, '', '411180564@qq.com', html_message=html_message,
                  recipient_list=[email])