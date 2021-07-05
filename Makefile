# Full path to prevent from using aliases
CP = /bin/cp
EZ_LIB_DIR = /usr/lib/easy-flamegraph
EZ_COND_DIR = /usr/lib/easy-flamegraph/conditions
EZ_COND_DIR_IO = /usr/lib/easy-flamegraph/conditions/io
EZ_COND_DIR_MEM = /usr/lib/easy-flamegraph/conditions/mem
EZ_SYSINFO_DIR = /usr/lib/easy-flamegraph/sysinfo
EZ_LOG_DIR = /var/log/easy-flamegraph
EZ_DEFAULT_DIR = /etc/default/
EZ_CRON_DIR = /etc/cron.d/
INSTALL = install
INSTALL_DATA = ${INSTALL} -m 644
INSTALL_BIN = ${INSTALL} -m 755

install:
	mkdir -p $(DESTDIR)$(EZ_LIB_DIR)
	mkdir -p $(DESTDIR)$(EZ_COND_DIR)
	mkdir -p $(DESTDIR)$(EZ_COND_DIR_IO)
	mkdir -p $(DESTDIR)$(EZ_COND_DIR_MEM)
	mkdir -p $(DESTDIR)$(EZ_SYSINFO_DIR)
	mkdir -p $(DESTDIR)$(EZ_LOG_DIR)
	mkdir -p $(DESTDIR)$(EZ_CRON_DIR)
	mkdir -p $(DESTDIR)$(EZ_DEFAULT_DIR)

	$(INSTALL_BIN) gen-flamegraph.sh $(DESTDIR)$(EZ_LIB_DIR)
	$(INSTALL_BIN) profile/entry $(DESTDIR)$(EZ_LIB_DIR)
	$(INSTALL_BIN) profile/lib $(DESTDIR)$(EZ_LIB_DIR)
	$(INSTALL_BIN) profile/ezcli $(DESTDIR)$(EZ_LIB_DIR)
	$(INSTALL_BIN) profile/conditions/cpu $(DESTDIR)$(EZ_COND_DIR)
	$(INSTALL_BIN) profile/conditions/io/io $(DESTDIR)$(EZ_COND_DIR_IO)
	$(INSTALL_BIN) profile/conditions/io/io_ftrace $(DESTDIR)$(EZ_COND_DIR_IO)
	$(INSTALL_BIN) profile/conditions/mem/mem $(DESTDIR)$(EZ_COND_DIR_MEM)
	$(INSTALL_BIN) profile/conditions/mem/mem_ftrace $(DESTDIR)$(EZ_COND_DIR_MEM)
	$(INSTALL_BIN) profile/sysinfo/bcache $(DESTDIR)$(EZ_SYSINFO_DIR)
	$(INSTALL_BIN) profile/sysinfo/irq-stat $(DESTDIR)$(EZ_SYSINFO_DIR)
	$(INSTALL_BIN) profile/sysinfo/mem-stat $(DESTDIR)$(EZ_SYSINFO_DIR)
	$(INSTALL_BIN) profile/sysinfo/net-stat $(DESTDIR)$(EZ_SYSINFO_DIR)
	$(INSTALL_BIN) profile/sysinfo/process-stat $(DESTDIR)$(EZ_SYSINFO_DIR)
	$(INSTALL_DATA) profile/easy-flamegraph.conf $(DESTDIR)$(EZ_DEFAULT_DIR)
	$(INSTALL_DATA) profile/easy-flamegraph-cron $(DESTDIR)$(EZ_CRON_DIR)

	git submodule update --init FlameGraph
	$(CP) -r ./FlameGraph/ $(DESTDIR)$(EZ_LIB_DIR)
	$(CP) /proc/version $(DESTDIR)$(EZ_LOG_DIR)

uninstall:
	rm -rf $(DESTDIR)$(EZ_LIB_DIR)/FlameGraph/
	rm -f $(DESTDIR)$(EZ_CRON_DIR)/easy-flamegraph-cron
	rm -f $(DESTDIR)$(EZ_DEFAULT_DIR)/easy-flamegraph.conf
	rm -f $(DESTDIR)$(EZ_LIB_DIR)/gen-flamegraph.sh
	rm -f $(DESTDIR)$(EZ_LIB_DIR)/entry
	rm -f $(DESTDIR)$(EZ_LIB_DIR)/ezcli
	rm -f $(DESTDIR)$(EZ_LIB_DIR)/lib
	rm -rf $(DESTDIR)$(EZ_LIB_DIR)/conditions
	rm -rf $(DESTDIR)$(EZ_LIB_DIR)/sysinfo
	rmdir --ignore-fail-on-non-empty $(DESTDIR)$(EZ_LIB_DIR)
