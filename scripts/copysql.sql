\copy tb_address (id,city,complement,country,number,state,street,zip_code) FROM 'tb_address.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy tb_card (id,cvv,expired,number) FROM 'tb_card.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy tb_role (id,authority) FROM 'tb_role.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

\copy tb_congresso (id,max_reviews_per_article,min_reviews_per_article,end_date,review_deadline,start_date,submission_deadline,congresso_modality,description,description_title,image_thumbnail,name,place) FROM 'tb_congresso.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8', FORCE_NULL (image_thumbnail));

\copy tb_user (id,is_reviewer,address_id,card_id,congresso_id,membership_number,login,password,username_user,work_place,profile_image) FROM 'tb_user.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8', FORCE_NULL (congresso_id,profile_image));

\copy tb_user_role (role_id,user_id) FROM 'tb_user_role.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

\copy tb_article (id,congresso_id,published_at,description,format,status,title,body) FROM 'tb_article.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8', FORCE_NULL (congresso_id));

\copy tb_articles_users (article_id,user_id) FROM 'tb_articles_users.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

\copy tb_evaluation (id,final_score,number_of_reviews,article_id) FROM 'tb_evaluation.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

\copy tb_review (id,score,article_id,create_at,evaluation_id,reviewer_id,comment) FROM 'tb_review.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8', FORCE_NULL (evaluation_id));
