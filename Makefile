#CP = /bin/cp
DESTDIR = $(CURDIR)/debian/tmp
#EZ_CONF_DIR = /etc/ez_flamegraph/ez_conf
EZ_LIB_DIR = /usr/lib/easy-flamegraph
EZ_LOG_DIR = /var/log/easy-flamegraph
EZ_CRON_DIR = /etc/cron.d/
INSTALL = install
INSTALL_DATA = ${INSTALL} -m 644
INSTALL_BIN = ${INSTALL} -m 755

install:
	mkdir -p $(DESTDIR)$(EZ_LIB_DIR)
	mkdir -p $(DESTDIR)$(EZ_LOG_DIR)
	mkdir -p $(DESTDIR)$(EZ_CRON_DIR)

	$(INSTALL_BIN) easy-flamegraph.sh $(DESTDIR)$(EZ_LIB_DIR)
	$(INSTALL_BIN) flamegraph-mem $(DESTDIR)$(EZ_LIB_DIR)
	$(INSTALL_DATA) ez-flamegraph $(DESTDIR)$(EZ_CRON_DIR)

uninstall:
	rm -f $(DESTDIR)$(EZ_CRON_DIR)/ez-flamegraph
	rm -f $(DESTDIR)$(EZ_LIB_DIR)/easy-flamegraph.sh
	rm -f $(DESTDIR)$(EZ_LIB_DIR)/flamegraph-mem
	rmdir --ignore-fail-on-non-empty $(DESTDIR)$(EZ_LIB_DIR)
