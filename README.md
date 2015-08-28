BoardTester - collect data with automated hardware power cycling



broaster 

    The Board Roaster. Turn on a board, get data, turn off board.
    Repeat and analyze the results.

![broaster screenshot](/docs/broaster.png "broaster screenshot")

camids 

    IDS uEye USB camera tester. Use a relay to simulate the plugging in
    of a IDS camera, start the uEye cockpit software, take a screenshot.
    Repeat. Store the data for later analysis.


![camids screenshot](/docs/camids.png "camids screenshot")


process

    Process the results. Create text and graphical summaries of test
    results from the broaster or camids.


visualize

    Provide a gui for visualizing broaster results.

visualize Insllation:
    
    Instructions for installing guiqwt in virtualenv:

    source the virtualenv/bin/activate

    Download the 2.3.2 release:
        wget https://github.com/PierreRaybaut/guiqwt/\
                archive/v2.3.2.tar.gz

    python setup.py install
    pip install guidata

    Which will then through an error: from:
    venv/lib/python2.7/site-packages/spyderlib/qt/__init__.py

Notes:
    Are you seeing messages like:

    ValueError: API 'QDate' has already been set to version 1

    Or:

    cannot import name SIGNAL

   
    Don't install from pip, download the versions as described above and
    compile them directly. Don't go for the newest versions though, as 
    of this writing (20150827), the development release is wiggling the
    axis on static images. It's exactly what it sounds like.



The steps required for pyqt and guiqwt installation in virtualenv
matching the python xy configuration that seems reliable on ms windows
is:

Fedora Core 22

    sudo dnf install gcc
    sudo dnf install gcc-c++
    sudo dnf install qt4-devel
    sudo dnf install qdevelop

    These are required for spyderlib, which makes running the guiqwt
    tests possible.
    sudo dnf install -y lapack lapack-devel blas blas-devel
    sudo dnf install -y blas-static lapack-static 
    sudo dnf install -y hdf5-devel


    virtualenv venvpyqt4
    source venvpyqt4/bin/activate
    
    wget 'http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.9/\
        sip-4.16.9.tar.gz'
    tar -zxvf sip-4.16.9.tar.gz
    cd sip-4.16.9
    python configure.py --incdir=${VIRTUAL_ENV}/include
    make -j2
    make install

    wget 'http://downloads.sourceforge.net/project/pyqt/PyQt4/PyQt-4.11.4/\
        PyQt-x11-gpl-4.11.4.tar.gz'
    tar -zxvf PyQt-x11-gpl-4.11.4.tar.gz
    cd PyQt-x11-gpl-4.11.4/
    python configure.py -q /usr/bin/qmake-qt4
    type "yes" to accept license
    make -j2
    make install
   
    Verify the installation by viewing the installed version strings: 
    python
    import sip; print sip.SIP_VERSION_STR
    from PyQt4 import QtCore; print QtCore.PYQT_VERSION_STR

    Now Install the guiqwt prerequisites
    pip install numpy
    pip install cython
    pip install scipy
    pip install h5py

    Spyder older version required version:
    wget 'https://bitbucket.org/spyder-ide/spyderlib/downloads/\
            spyder-2.3.5.2.zip'
    unzip spyder-2.3.5.2.zip
    cd spyder-2.3.5.2/
    python setup.py install


    PyQwt is required for guiqwt
    wget 'http://downloads.sourceforge.net/project/pyqwt/pyqwt5/\
            PyQwt-5.2.0/PyQwt-5.2.0.tar.gz'
    tar -zxvf PyQwt-5.2.0.tar.gz
    cd PyQwt-5.2.0
    cd configure
    python configure.py -Q ../qwt-5.2
    make
    make install

    Grab the 1.6.1 version of guidata
    wget https://github.com/PierreRaybaut/guidata/archive/v1.6.1.tar.gz
    tar -zxvf v1.6.1.tar.gz
    cd guidata-1.6.1/
    python setup.py install

    Grab the 2.3.2 version of qwt:
    wget https://github.com/PierreRaybaut/guiqwt/archive/v2.3.2.tar.gz
    tar -zxvf v2.3.2.tar.gz
    cd guiqwt-2.3.2/
    python setup.py build install
    
    # Now run the guiqwt visualization tests, make sure there are no
    # 'wiggles' when double clicking the hist2d example. Make sure to
    # run the commands below NOT in the guiqwt download directory.
    python
    from guiqwt import tests
    tests.run()
    
