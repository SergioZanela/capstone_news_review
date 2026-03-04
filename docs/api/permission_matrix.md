Endpoint permissions:

GET /api/articles/                  -> all roles (approved only)
GET /api/articles/subscribed/        -> reader only
GET /api/articles/<id>/              -> all roles (approved only unless editor/journalist rules allow more)
POST /api/articles/                  -> journalist only
PUT /api/articles/<id>/              -> journalist/editor
DELETE /api/articles/<id>/           -> journalist/editor
POST /api/articles/<id>/approve/     -> editor only