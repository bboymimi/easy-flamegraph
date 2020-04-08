#CP = /bin/cp
#DESTDIR = /usr/lib/
#EZ_CONF_DIR = /etc/ez_flamegraph/ez_conf
# Full path to prevent from using aliases
CP = /bin/cp
EZ_LIB_DIR = /usr/lib/easy-flamegraph
EZ_LOG_DIR = /var/log/easy-flamegraph
EZ_DEFAULT_DIR = /etc/default/
EZ_CRON_DIR = /etc/cron.d/
INSTALL = install
INSTALL_DATA = ${INSTALL} -m 644
INSTALL_BIN = ${INSTALL} -m 755

install:
	mkdir -p $(DESTDIR)$(EZ_LIB_DIR)
	mkdir -p $(DESTDIR)$(EZ_LOG_DIR)
	mkdir -p $(DESTDIR)$(EZ_CRON_DIR)
	mkdir -p $(DESTDIR)$(EZ_DEFAULT_DIR)

	$(INSTALL_BIN) easy-flamegraph.sh $(DESTDIR)$(EZ_LIB_DIR)
	$(INSTALL_BIN) flamegraph-cpu $(DESTDIR)$(EZ_LIB_DIR)
	$(INSTALL_BIN) flamegraph-entry $(DESTDIR)$(EZ_LIB_DIR)
	$(INSTALL_BIN) flamegraph-mem $(DESTDIR)$(EZ_LIB_DIR)
	$(INSTALL_BIN) flamegraph-io $(DESTDIR)$(EZ_LIB_DIR)
	$(INSTALL_DATA) easy-flamegraph $(DESTDIR)$(EZ_DEFAULT_DIR)
	$(INSTALL_DATA) ez-flamegraph $(DESTDIR)$(EZ_CRON_DIR)

	git submodule update --init FlameGraph
	$(CP) -r ./FlameGraph/ $(DESTDIR)$(EZ_LIB_DIR)

uninstall:
	rm -rf $(DESTDIR)$(EZ_LIB_DIR)/FlameGraph/
	rm -f $(DESTDIR)$(EZ_CRON_DIR)/ez-flamegraph
	rm -f $(DESTDIR)$(EZ_DEFAULT_DIR)/easy-flamegraph
	rm -f $(DESTDIR)$(EZ_LIB_DIR)/easy-flamegraph.sh
	rm -f $(DESTDIR)$(EZ_LIB_DIR)/flamegraph-io
	rm -f $(DESTDIR)$(EZ_LIB_DIR)/flamegraph-mem
	rm -f $(DESTDIR)$(EZ_LIB_DIR)/flamegraph-entry
	rm -f $(DESTDIR)$(EZ_LIB_DIR)/flamegraph-cpu
	rmdir --ignore-fail-on-non-empty $(DESTDIR)$(EZ_LIB_DIR)
