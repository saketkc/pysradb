

############
download
############

All the `.sra` files belonnging to a certain project can be downloaded using ``download``:

::

    $ pysradb download -y -t 8 -p SRP002605
    
 
``pysradb`` also supports faster downloading of `.sra/.fastq` files using UDP protocol if `aspera-client <https://downloads.asperasoft.com/connect2/>`_ is installed:

:: 

    $ wget -c https://download.asperasoft.com/download/sw/connect/3.9.9/ibm-aspera-connect-3.9.9.177872-linux-g2.12-64.tar.gz
    $ tar -zxvf ibm-aspera-connect-3.9.9.177872-linux-g2.12-64.tar.gz && ls
    $ bash ibm-aspera-connect-3.9.9.177872-linux-g2.12-64.sh


    $ pysradb download --use_ascp -y -t 8 -p SRP002605

It is also possible to pipe the output of ``metadata`` to download:

::

   $ pysradb metadata --detailed SRP098789 | pysradb download


