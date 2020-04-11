# Full path to prevent from using aliases
CP = /bin/cp
EZ_LIB_DIR = /usr/lib/easy-flamegraph
EZ_COND_DIR = /usr/lib/easy-flamegraph/conditions
EZ_LOG_DIR = /var/log/easy-flamegraph
EZ_DEFAULT_DIR = /etc/default/
EZ_CRON_DIR = /etc/cron.d/
INSTALL = install
INSTALL_DATA = ${INSTALL} -m 644
INSTALL_BIN = ${INSTALL} -m 755

install:
	mkdir -p $(DESTDIR)$(EZ_LIB_DIR)
	mkdir -p $(DESTDIR)$(EZ_COND_DIR)
	mkdir -p $(DESTDIR)$(EZ_LOG_DIR)
	mkdir -p $(DESTDIR)$(EZ_CRON_DIR)
	mkdir -p $(DESTDIR)$(EZ_DEFAULT_DIR)

	$(INSTALL_BIN) gen-flamegraph.sh $(EZ_LIB_DIR)
	$(INSTALL_BIN) entry $(EZ_LIB_DIR)
	$(INSTALL_BIN) lib $(EZ_LIB_DIR)
	$(INSTALL_BIN) conditions/cpu $(EZ_COND_DIR)
	$(INSTALL_BIN) conditions/mem $(EZ_COND_DIR)
	$(INSTALL_BIN) conditions/io $(EZ_COND_DIR)
	$(INSTALL_BIN) conditions/bcache $(EZ_COND_DIR)
	$(INSTALL_DATA) easy-flamegraph.conf $(EZ_DEFAULT_DIR)
	$(INSTALL_DATA) easy-flamegraph-cron $(EZ_CRON_DIR)

	git submodule update --init FlameGraph
	$(CP) -r ./FlameGraph/ $(DESTDIR)$(EZ_LIB_DIR)

uninstall:
	rm -rf $(EZ_LIB_DIR)/FlameGraph/
	rm -f $(EZ_CRON_DIR)/easy-flamegraph-cron
	rm -f $(EZ_DEFAULT_DIR)/easy-flamegraph.conf
	rm -f $(EZ_LIB_DIR)/gen-flamegraph.sh
	rm -f $(EZ_LIB_DIR)/entry
	rm -rf $(EZ_LIB_DIR)/conditions
	rmdir --ignore-fail-on-non-empty $(EZ_LIB_DIR)
