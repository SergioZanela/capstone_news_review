Entities:
- CustomUser (role: reader/editor/journalist)
- Publisher
- Article
- Newsletter

Relationships:
- Publisher M2M CustomUser (editors)
- Publisher M2M CustomUser (journalists)

- CustomUser (journalist) 1..* Article (author)
- Article 0..1 Publisher (publisher)

Constraint:
- Article must be either:
  A) Independent: publisher = NULL, author.role = journalist
  B) Publisher content: publisher != NULL, author.role = journalist

- Newsletter *..* Article (many-to-many)
- CustomUser (journalist/editor) 1..* Newsletter (author)

Subscriptions (Reader only):
- CustomUser (reader) M2M Publisher (subscribed_publishers)
- CustomUser (reader) M2M CustomUser (subscribed_journalists)