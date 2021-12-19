all: 

.PHONY: clean
clean:
	rm -rf .venv

.PHONY: deps
deps: 
	./install-deps.sh

.PHONY: venv
venv:
	( \
		python3 -m venv --system-site-packages .venv; \
		. ./.venv/bin/activate; \
		python3 -m pip install --upgrade pip; \
		python3 -m pip install --upgrade -r ./requirements.txt; \
		python3 -m pip install --upgrade -r ./requirements-dev.txt; \
	)

.PHONY: install
install: 
	./install-deps.sh
	mkdir -p /usr/lib/geekworm/X715_fan
	install --group gpio --owner root --mode 0644 ./requirements.txt /usr/lib/geekworm/X715_fan
	( \
		cd /usr/lib/geekworm/X715_fan; \
		python3 -m venv --system-site-packages .venv; \
		. ./.venv/bin/activate; \
		python3 -m pip install --upgrade pip; \
		python3 -m pip install --upgrade -r ./requirements.txt; \
		cd -; \
	)
	install --group gpio --owner root --mode 0744 ./X715_fan.py /usr/lib/geekworm/X715_fan
	install --group root --owner root --mode 0755 ./X715_fan.service /etc/systemd/system
	systemctl daemon-reload
	systemctl enable X715_fan
	service X715_fan start

.PHONY: remove
remove:
	service X715_fan stop
	systemctl disable X715_fan
	rm -f /etc/systemd/system/X715_fan.service
	systemctl daemon-reload
	rm -rf /usr/lib/geekworm/X715_fan