TARGETS := $(MAKECMDGOALS)

.PHONY: all $(TARGETS)
all: $(TARGETS)

$(TARGETS):
	mkapp -v -t $@ electricMonitoring.adef
	mkapp -v -t $@ $$LEGATO_ROOT/apps/platformServices/mqttClient/mqttClient.adef

clean:
	rm -rf _build_* *.update

