

A new way to build Django website. Get away from the initial boilerplate project and apps. Siteplan comes with CMS, e-commerce store, payment gateway, task queue and many more features commonly found in modern websites.

Start small, grow big.

## Quickstart
Create the app directory:-

```
mkdir myapp && cd myapp
python -mvenv venv
venv/bin/pip install -U siteplan --pre
```

Then run `siteplan`:-

```
venv/bin/siteplan run
```

It possible to add your own views (controller) and models for more control and but most of the time you just want to customize the templates when working with `siteplan`.

You can add your own templates directory in your app root:-

```
mkdir -p templates/siteplan
```