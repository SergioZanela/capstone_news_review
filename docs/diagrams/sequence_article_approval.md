Sequence: Article approval + notifications (Signals approach)

1) Journalist creates Article (approved = False)
2) Editor views review queue (unapproved articles)
3) Editor approves Article (approved becomes True)
4) Article is saved
5) post_save signal runs (only when approved changes False -> True)
6) Signal calls services:
   - EmailService: email approved article to subscribers
   - XService: POST approved article to X using requests
7) System logs success/failure (exceptions handled)