OpenTSDBReporter
----------------
The OpenTSDBReporter ZenPack enables the gathering and reporting of metrics 
from Zenoss source code.  It allows the "metrology" python library to write 
to an OpenTSDB database.  For information about OpenTSDB see opentsdb.net.


In order to collect data:
1) Install the OpenTsdbReporter ZenPack
 
2) Edit $ZENHOME/etc/global.conf to refer to an OpenTSDB instance.
    opentsdbreporter-host 10.87.110.191
    opentsdbreporter-port 4242
    opentsdbreporter-interval 60
 
3) Instrument the code using the metrology library.  Most likely to be useful 
are Counters, Gauges, and Timers. Read more at http://metrology.readthedocs.org/
 
4) Run the instrumented code.
 
5) View the metrics in OpenTSDB by pointing a web browser at the host:port 
that was set in step 2. 
