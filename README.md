# PMI of KCM

Use Pointwise mutual information (PMI), or point mutual information to 

## Install

* (Recommended): Use [docker-compose](https://github.com/udicatnchu/udic-nlp-api) to install

## Manually Install

If you want to integrate `PMIofKCM` into your own django project, use manually install.

* `pip install PMIofKCM`

### Config

1. add django app `PMIofKCM` in `settings.py`：

  - add this:

    ```
    INSTALLED_APPS=[
    ...
    ...
    ...
    'PMIofKCM',
    ]
    ```

2. add url patterns of PMIofKCM into `urls.py`：

  - add this:

    ```
    # pmiOfKcm
    import PMIofKCM.urls
    urlpatterns += [
        url(r'^pmi/', include(PMIofKCM.urls))
    ]
    ```

3. use `python3 manage.py buildPMI --lang <lang, e.g., zh or en or th> ` to build model of PMIofKCM.
4. fire `python manage.py runserver` and go `127.0.0.1:8000/` to check whether the config is all ok.

## API

1. the result of querying pmi model with keyword `周杰倫`(Captain America)：_`/pmi`_
  - keyword
  - num (default=10)
  - keyFlag (default=[])
  - valueFlag (defualt=[])
  - example1：[http://udiclab.cs.nchu.edu.tw/pmi?keyword=周杰倫](http://udiclab.cs.nchu.edu.tw/pmi?keyword=周杰倫)

      ```
      
      ```

## Deployment

PMIofKCM is a django-app, so depends on django project.

## Built With

* python3.5
* pymongo

## Contributors

* **陳聖軒**
* **張泰瑋** [david](https://github.com/david30907d)

## License

This package use `GPL3.0` License.