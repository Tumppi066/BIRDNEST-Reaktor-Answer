Start nginx.exe and the backend. This will publish your website to http port 40080 or https port 40443.
You will need your own ssl certificates and keys for https. These can be placed in conf and should be named cert.pem and cert.key respectively.
> You can change between the versions by commenting / uncommenting the configs in /conf/nginx.conf

> You will also need to change the addresses in index.js, to what your website name is (default is for my personal deployment)