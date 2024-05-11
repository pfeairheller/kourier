
.PHONY: build-kourier
build-kourier:
#	@podman buildx build --platform=linux/amd64 -f images/keripy.base.dockerfile --tag weboftrust/keri.base .
	@podman buildx build --platform=linux/arm64 -f images/kourier-arm64.dockerfile --tag weboftrust/kourier:arm64 .

.PHONY: publish-keri
publish-keri:
	@docker push weboftrust/keri --all-tags
