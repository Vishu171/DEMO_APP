**Table 1: FINANCIALS.MARVELL_DEMO.INVENTORY_ACTUALS (Stores Actual Inventory ITEM information for  Different Types in previous quarters)
 
- ITEM_WID			-	Unique ID for an ITEM. This column refers to ITEM_WID in table FINANCIALS.MARVELL_DEMO.ITEM_DETAILS. Column alias is ITEM WID
- AMOUNT			-  	Amount associated with the ITEM , Inventory Value in $. Column alias is AMOUNT and type os currency
- QUARTER_NAME			-  	Quarter when Item actual inventory was recorded. Column alias is QUARTER NAME
- TYPE				-  	Type of Inventory for Actual Items. Column alias is TYPE


**Table 2: FINANCIALS.MARVELL_DEMO.INVENTORY_ON_HANDS (Stores inventory on hand for future quarters and the inventory on hand as of end of quarters for previous quarters)
 
- ITEM_WID			-  	Unique ID for an ITEM. This column refers to ITEM_WID in table FINANCIALS.MARVELL_DEMO.ITEM_DETAILS. Column alias is ITEM WID
- AMOUNT			-  	Amount associated with the ITEM, Inventory Value in $. Column alias is ON-HAND AMOUNT and type os currency
- QUANTITY			-  	Number of ITEM Quantities recorded Per Quarter. Column alias is QUANTITY
- QUARTER_NAME			-  	Quarter when Item inventory was populated. Column alias is QUARTER NAME
- CUM_YIELD			-  	Cummulative Yield for an Item. Column alias is CUMULATIVE YIELD
- YIELD_QUANTITY 		-  	"Quantity Yield" for an Item per Quarter against Number of ITEM Quantity. Column alias is YIELD QUANTITY


**Table 3: FINANCIALS.MARVELL_DEMO.ITEM_DETAILS (This is ITEM master table stores ITEM Information including their Item WID, Division,BU, ProductLine ETC.)

- ITEM_WID 			-	Unique ID for an ITEM. Column alias is ITEM WID
- COMPANY                       -	NAME of the company Item belongs to. Column alias is COMPANY
- DIVISION                      -	Division In the company Item belongs to. Column alias is DIVISION
- BU                            -	BU In the company Item belongs to, Interchangeable called Organization. Column alias is BU
- PRODUCT_LINE                  -	Product Line In the company Item belongs to. Column alias is PRODUCT LINE
- SUB_PRODUCT_LINE              -	Sub Product Line In the company Item belongs to. SUB PRODUCT LINE
- FINANCIAL_GROUP               -	Financial Group In the company Item belongs to. Column alias is FINANCIAL GROUP. 
- PART_NUMBER                   -	Part Number for an ITEM. Column alias is PART NUMBER
- ITEM_STAGE                    -	Stage in which Item is currently in Product Life Cycle. Column alias is ITEM STAGE. One of the values is FG that stands for Finished Goods
- ASSY_PART_NUMBER              -	Number when the part of Item is in Assembly stage. Column alias is ASSEMBLY PART NUMBER
- DIE_PART_NUMBER               -	Number when the part of Item is in Die stage. Column alias is DIE PART NUMBER
- ECCN                          -	ECCN Number for an Item to determine licencing information. Column alias is ECCN
- FAB_PART_NUMBER               -	Number when the part of Item is in FAB stage. Column alias is FAB PART NUMBER
- SCHEDULE_B_NUM                -	Specific Classification Code for Exporting Goods. Column alias is CLASSIFICATION CODE
- TEST_PART_NUMBER              -	Number when the part of Item is in Test stage. Column alias is TEST PART NUMBER
- PLATFORM                      -	Column alias is PLATFORM
- BASE_DIE                      -	Item Id for the Die. Column alias is BASE DIE
- BASE_DIE_REV                  -	Revised Item Id for the Die. Column alias is BASED DIE REVISED ID
- FAB_HOUSE                     -	Fabrication House Name for the Item. Column alias is FAB HOUSE
- DESIGN_COUNTRY                -	Country Name where the Item is Designed. Column alias is DESIGN COUNTRY
- MARKETING_ITEM                -	Item Number Associated for  Marketting Reference. Column alias is MARKETING ITEM NUMBER
- ITEM_TYPE                     -	Type of Item or Item category. Column alias is ITEM TYPE
- PLANNER_CODE                  -	PLanner Code for an Item which are up to date with Factory Status. Column alias is PLANNER CODE
- INVENTORY_ORGANIZATION        -	Unique Number of Inventory Organization. Column alias is INVENTORY ORGANIZATION
- COUNTRY_OF_MANUFACTURING      -	Country where Item is Manufactured. Column alias is MANUFACTURING COUNTRY
- DEVICE                        -	Device Name of the Item. Column alias is DEVICE
- PRODUCT_GROUP                 -	"Type of Product" or product group with list of allowed values Wfr, IC and MD where Wfr stands for Wafer, IC stands for Integrated Circuit and MD stands for Mechanical Devices. Column alias is PRODUCT GROUP
- PROJECT_CODE                  -	Project Code Associated with an Item. Column alias is PROJECT CODE
- PROJECT_CODE_DESCRIPTION      -	Description of a Project Code. Column alias is PROJECT CODE DESCRIPTION
- PACKAGE_CODE                  -	Package Code for an Item. Column alias is PACKAGE CODE
- SERVICE_PART_NUMBER           -	Service Part Number for an Item. Column alias is SERVICE PART NUMBER
- LICENSE_EXCEPTION             -	Export Licence Exception Number for the Item. Column alias is LICENSE EXCEPTION
- END_MARKET                    -	Describes which category of Market Item belongs to during Sale. Column alias is END MARKET
- SUB_MARKET 			-	Describes which Sub category of Market Item belongs to during Sale. Column alias is SUB MARKET
- MODEL_NUMBER       		-	Model Number for an ITEM. Column alias is MODEL NUMBER
- SPEED                         -	Speed for an Item from performance Characteristics. Column alias is SPEED
- ITEM_TYPE_GROUP               -	Item Group Type for an Item Listed. Column alias is ITEM TYPE GROUP
- MPR_YEAR_CATEGORY             -	MPR YEAR CATEGORY for an Item. Column alias is MPR YEAR CATEGORY
- MPR_YEAR_CATEGORY_GROUP       -	Year Categroy Group for MPR. Column alias is MPR YEAR CATEGORY GROUP
- MPR_YEAR_CATEGORY_SORTING     -	Column alias is MPR YEAR CATEGORY SORTING
- CURRENT_MODEL_NUMBER          -	Current Model Number for an ITEM. Column alias is CURRENT MODEL NUMBER
- SALES_COMP_DIVISION           -	Division for the Sales Team doing the Sales for an ITEM. Column alias is SALES COMP DIVISION 
- SALES_COMP_BU                 -	BU or Organization for the Sales Team doing the Sales for an ITEM. Column alias is SALES COMP BU
- SALES_COMP_PRODUCT_LINE       -	Product Line for the Sales Team doing the Sales for an ITEM. Column alias is SALES COMP PRODUCT LINE
- SALES_COMP_FINANCIAL_GROUP    -	Financial Group for the Sales Team doing the Sales for an ITEM. Column alias is SALES COMP FINANCIAL GROUP
- SALES_COMP_SUB_PRODUCT_LINE   -	Sub Product Line for the Sales Team doing the Sales for an ITEM. Column alias is SALES COMP SUB PRODUCT LINE
- TECHNOLOGY_GROUP              -	Tech Group for an ITEM parts. Column alias is TECHNOLOGY GROUP.This Column may also be referred as Tech Group. Values in this column generally have format starting with number and followed by string nm for example 80nm_90nm or 7nm and so on
- IDENTIFIED_IP                 -	Intellectual property for an Item. Column alias is IDENTIFIED IP
- BUSINESS_OWNER                -	Busines owner of the ITEM. Column alias is BUSINESS OWNER
- PRODUCT_LINE_MANAGER          -	Line Manager for an ITEM. Column alias is PRODUCT LINE MANAGER


**Table 4: FINANCIALS.MARVELL_DEMO.PROJECTED_INVENTORY (Stores projected inventory for future quarters with type of projected inventory)

- ITEM_WID			-   	Unique ID for an ITEM. This column refers to ITEM_WID in table FINANCIALS.MARVELL_DEMO.ITEM_DETAILS. Column alias is ITEM WID
- AMOUNT			-	Amount associated with the ITEM	, Inventory Value in $. Column alias is AMOUNT and type os currency
- QUARTER_NAME			-   	Quarter when Item inventory	was populated. Column alias is QUARTER NAME
- TYPE				-   	Type of Inventory for Projected Items. Column alias is TYPE
