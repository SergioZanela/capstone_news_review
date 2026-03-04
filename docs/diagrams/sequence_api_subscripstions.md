Sequence: Reader requests subscribed articles via API

1) Reader authenticates (JWT token)
2) Reader calls GET /api/articles/subscribed/
3) API validates token + role (must be reader)
4) API loads reader subscriptions:
   - subscribed_publishers
   - subscribed_journalists
5) API queries approved articles that match those subscriptions
6) API returns serialized list of articles