cd k8s

helm upgrade --install telewalker-379760 . \
  --set phone="+79933379760" \
  --set phone_suffix="379760" \
  --set api_id="23006720" \
  --set api_hash="dd0ca37e3ffa595a4e6490f0461921a7" \
  --set channel="THEODDSPRODIGY" \
  --set image="telewalker:latest"
