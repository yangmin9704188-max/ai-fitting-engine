.PHONY: help sync-dry sync ai-prompt ai-prompt-json curated_v0_round

# Default target
help:
	@echo "Available targets:"
	@echo "  make sync-dry ARGS=\"--set snapshot.status=candidate\""
	@echo "  make sync ARGS=\"--set last_update.trigger=manual_test\""
	@echo "  make ai-prompt"
	@echo "  make ai-prompt-json"
	@echo "  make curated_v0_round RUN_DIR=<out_dir> [SKIP_RUNNER=1]"
	@echo ""
	@echo "Examples:"
	@echo "  make sync-dry ARGS=\"--set snapshot.status=candidate\""
	@echo "  make sync ARGS=\"--set snapshot.status=hold --set last_update.trigger=test\""
	@echo "  make ai-prompt"
	@echo "  make ai-prompt-json"
	@echo "  make curated_v0_round RUN_DIR=verification/runs/facts/curated_v0/round20_20260125_164801"
	@echo "  make curated_v0_round RUN_DIR=verification/runs/facts/curated_v0/round20_20260125_164801 SKIP_RUNNER=1"

sync-dry:
	python tools/sync_state.py --dry-run $(ARGS)

sync:
	python tools/sync_state.py $(ARGS)

ai-prompt:
	python tools/render_ai_prompt.py

ai-prompt-json:
	python tools/render_ai_prompt.py --format json

# Round execution wrapper
curated_v0_round:
	@if [ -z "$(RUN_DIR)" ]; then \
		echo "Error: RUN_DIR is required. Usage: make curated_v0_round RUN_DIR=<out_dir>"; \
		exit 1; \
	fi
	@if [ "$(SKIP_RUNNER)" != "1" ]; then \
		if [ ! -f "$(RUN_DIR)/facts_summary.json" ]; then \
			echo "Running curated_v0 facts runner..."; \
			python verification/runners/run_curated_v0_facts_round1.py \
				--npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz \
				--out_dir $(RUN_DIR); \
		else \
			echo "facts_summary.json already exists in $(RUN_DIR), skipping runner."; \
			echo "To force re-run, delete $(RUN_DIR)/facts_summary.json or run without SKIP_RUNNER=1"; \
		fi \
	else \
		echo "SKIP_RUNNER=1: Skipping runner execution."; \
	fi
	@echo "Running postprocess_round.py (always executed)..."
	@python tools/postprocess_round.py --current_run_dir $(RUN_DIR) || true
