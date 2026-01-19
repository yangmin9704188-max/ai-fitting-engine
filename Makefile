.PHONY: help sync-dry sync ai-prompt ai-prompt-json

# Default target
help:
	@echo "Available targets:"
	@echo "  make sync-dry ARGS=\"--set snapshot.status=candidate\""
	@echo "  make sync ARGS=\"--set last_update.trigger=manual_test\""
	@echo "  make ai-prompt"
	@echo "  make ai-prompt-json"
	@echo ""
	@echo "Examples:"
	@echo "  make sync-dry ARGS=\"--set snapshot.status=candidate\""
	@echo "  make sync ARGS=\"--set snapshot.status=hold --set last_update.trigger=test\""
	@echo "  make ai-prompt"
	@echo "  make ai-prompt-json"

sync-dry:
	python tools/sync_state.py --dry-run $(ARGS)

sync:
	python tools/sync_state.py $(ARGS)

ai-prompt:
	python tools/render_ai_prompt.py

ai-prompt-json:
	python tools/render_ai_prompt.py --format json
