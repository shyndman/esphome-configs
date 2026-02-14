# Activate this project's virtual environment when entering the directory.
if [[ -z "${VIRTUAL_ENV:-}" && -f ".venv/bin/activate" ]]; then
  source ".venv/bin/activate"
fi

# Deactivate when leaving this directory.
autoenv_leave_handler() {
  if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    deactivate
  fi
}
