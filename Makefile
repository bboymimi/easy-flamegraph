#CP = /bin/cp
#DESTDIR = /usr/lib/
#EZ_CONF_DIR = /etc/ez_flamegraph/ez_conf
EZ_LIB_DIR = /usr/lib/easy-flamegraph
EZ_LOG_DIR = /var/log/easy-flamegraph
EZ_CRON_DIR = /etc/cron.d/
INSTALL = install
INSTALL_DATA = ${INSTALL} -m 644
INSTALL_BIN = ${INSTALL} -m 755

install:
	mkdir -p $(EZ_LIB_DIR)
	mkdir -p $(EZ_LOG_DIR)
	mkdir -p $(EZ_CRON_DIR)

	$(INSTALL_BIN) easy-flamegraph.sh $(EZ_LIB_DIR)
	$(INSTALL_BIN) flamegraph-mem $(EZ_LIB_DIR)
	$(INSTALL_DATA) ez-flamegraph $(EZ_CRON_DIR)

uninstall:
	rm -f $(EZ_CRON_DIR)/ez-flamegraph
	rm -f $(EZ_LIB_DIR)/easy-flamegraph.sh
	rm -f $(EZ_LIB_DIR)/flamegraph-mem
	rmdir --ignore-fail-on-non-empty $(EZ_LIB_DIR)
