########################################
# MySQL  - yummly
#  table creation scripts
########################################

DROP TABLE if exists records;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS INGREDIENTS;
DROP TABLE if exists units;
DROP TABLE if exists recipeingredients;
DROP VIEW if exists bakingrecipes;
DROP VIEW if exists bakingrecords;
DROP VIEW if exists formatrecipes;

########################
# Create records table
########################

CREATE TABLE records
(
  id  char(200) NOT NULL,
  rating  float,
  totaltime int,  
  name char(100),
  sourcename varchar(50),
  sourceurl varchar(250),
  servings int,
  PRIMARY KEY (id)
) ENGINE = InnoDB;


#####################
# Create recipe table
#####################

CREATE TABLE ingredients (
  ingredient char(50) NOT NULL,
  normingredient char(50),
  PRIMARY KEY (ingredient)
) ENGINE = InnoDB;

CREATE TABLE recipeingredients (
  id char(200) NOT NULL,
  ingredient char(50) NOT NULL,
  PRIMARY KEY (id, ingredient)
) ENGINE = InnoDB;


CREATE TABLE recipejaccard (
  id1 char(200) NOT NULL,
  id2 char(200) NOT NULL,
  jaccard float,
  PRIMARY KEY (id1, id2)
) ENGINE = InnoDB;

#########################
# Create ingredients table
#########################
CREATE TABLE recipes (
  id char(200) NOT NULL,
  ingredientLine varchar(200) NOT NULL,
  ingredient char(50),
  unit varchar(50),
  count int,
  PRIMARY KEY(id, ingredientLine)
) ENGINE=InnoDB;


#########################
# Create units table
#########################
CREATE TABLE units (
  keyword char(50) NOT NULL,
  unit varchar(50),
  PRIMARY KEY(keyword)
) ENGINE=InnoDB;



#####################
# Define foreign keys
#####################
CREATE VIEW searchrecords AS SELECT * FROM records WHERE id REGEXP '.*banana.*bread.*';
CREATE VIEW bakingrecipes AS SELECT * FROM recipes WHERE id REGEXP '.*banana.*bread.*';
#ALTER TABLE orderitems ADD CONSTRAINT fk_orderitems_orders FOREIGN KEY (order_num) REFERENCES orders (order_num);
#ALTER TABLE orderitems ADD CONSTRAINT fk_orderitems_products FOREIGN KEY (prod_id) REFERENCES products (prod_id);
#ALTER TABLE orders ADD CONSTRAINT fk_orders_customers FOREIGN KEY (cust_id) REFERENCES customers (cust_id);
#ALTER TABLE products ADD CONSTRAINT fk_products_vendors FOREIGN KEY (vend_id) REFERENCES vendors (vend_id);