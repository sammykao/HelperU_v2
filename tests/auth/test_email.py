import smtplib, ssl

sender = "info@helperu.com"
receiver = "kaosam77@gmail.com"   # replace with an inbox you control
app_password = "bnkcvcvkrbiqzoxd"  # no spaces

try:
    print("Sending email...")
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 587, context=context) as server:
        server.login(sender, app_password)
        server.sendmail(
            sender,
            receiver,
            "Subject: Gmail SMTP Test\n\nIf you see this, Gmail SMTP works!"
        )
    print("✅ Email sent successfully")
except Exception as e:
    print("❌ Error:", e)
