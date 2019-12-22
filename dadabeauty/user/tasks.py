from django.core.mail import send_mail

from dadabeauty.celery import app

@app.task

def send_active_mail(email, code_url):
    subject = 'DaDa-Beauty用户激活邮件'
    html_message = '''
        <p>亲爱的DaDa-Beauty用户：</p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;感谢注册达达美妆！</p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;激活地址为<a href='%s' target='blank'>点击激活</a></p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;Let's together to feel the charming world and beautify our marvelous life!</p>
        ''' % (code_url)
    send_mail(subject, '', 'dadabeauty1908@163.com.com', html_message=html_message, recipient_list=[email])