########################################
# MySQL  - yummly
#  table creation scripts
########################################

DROP TABLE if exists records;
DROP TABLE IF EXISTS RECIPES;
DROP TABLE IF EXISTS INGREDIENTS;


########################
# Create records table
########################

CREATE TABLE records
(
  id  char(200) NOT NULL,
  rating  float,
  totaltime int,  
  name char(100),
  source char(250),
  PRIMARY KEY(ID)
) ENGINE=InnoDB;


#####################
# Create recipe table
#####################

CREATE TABLE recipes (
  id  char(200) NOT NULL,
  ingredient char(50) NOT NULL,
  quantity char(250),
  PRIMARY KEY (id, ingredient)
) ENGINE = InnoDB;


#########################
# Create ingredients table
#########################
CREATE TABLE ingredients (
  name char(50) NOT NULL,
  unit char(10),
  PRIMARY KEY(name)
) ENGINE=InnoDB;



#####################
# Define foreign keys
#####################
#ALTER TABLE orderitems ADD CONSTRAINT fk_orderitems_orders FOREIGN KEY (order_num) REFERENCES orders (order_num);
#ALTER TABLE orderitems ADD CONSTRAINT fk_orderitems_products FOREIGN KEY (prod_id) REFERENCES products (prod_id);
#ALTER TABLE orders ADD CONSTRAINT fk_orders_customers FOREIGN KEY (cust_id) REFERENCES customers (cust_id);
#ALTER TABLE products ADD CONSTRAINT fk_products_vendors FOREIGN KEY (vend_id) REFERENCES vendors (vend_id);