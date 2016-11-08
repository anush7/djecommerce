# Djecommerce - Django e-commerce app

e-commerce app with all the basic features: 

* Products, product-variants, categories, attributes, export, import.
* Cart, order, checkout, payment-getway.
* Graphical Statistics on revenue and products.
* User - account, orders, addresses, profile.
* Create staff, staff management using roles(permissions).
* settings - Tax, shipping & currency
* product search, product search in category

### Installing

Install postgresql 9.5:

```
sudo apt-get install libpq-dev postgresql postgresql-contrib
```

create a new database. Enter the db details in the config.cfg file:

```
djecommerce/djecommerce/config.cfg
```

create braintree sandbox account(free), mailgun account and enter the respective details in the access_settings.py file:

```
djecommerce/djecommerce/settings/access_settings.py
```

Install rabbitmq server(used with celery):

```
sudo apt-get install rabbitmq-server
```

Install the requirements in requirements.txt file:

```
pip install -r requirements.txt
```

Next

```
python manage.py migrate
python manage.py runserver
```

## Built With

* Python
* django - 1.9.6
* Jquery
* Ajax
* postgresql 9.5
* Celery
* braintree - payment gateway
* mailgun

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
