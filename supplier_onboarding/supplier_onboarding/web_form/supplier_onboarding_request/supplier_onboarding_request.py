from frappe import new_doc, msgprint, db, throw
from frappe.model.document import Document

def get_context(context):
    # You can add custom context variables here, if needed.
    # For example:
    # context["custom_variable"] = "Hello, world!"
    return context

class SupplierOnboardingRequest(Document):
    def validate(self):
        # Add any validation logic here
        pass

    def on_submit(self):
        """This method is called when the document is submitted."""
        self.create_supplier()

    def on_cancel(self):
        """This method is called when the document is cancelled."""
        # Add logic to handle cancellation (e.g., reverse actions)
        pass  # Replace with your cancellation logic

    def create_supplier(self):
        # 1. Create a new Supplier document
        supplier = new_doc("Supplier")

        # 2. Copy basic information from Supplier Onboarding Request
        supplier.supplier_name = self.supplier_name
        supplier.contact_person = self.contact_person
        supplier.phone = self.phone
        supplier.email = self.email
        supplier.gstin = self.gstin
        supplier.pan = self.pan
        supplier.company = self.company  # Ensure you have company field in supplier doctype
        supplier.payment_terms = self.payment_terms_description

        try:
            supplier.save()
            db.commit()

            # 3. Create and link Addresses
            for address_data in self.addresses:
                self.create_address(supplier, address_data)
            db.commit()

            # 4. Create and link Contacts
            for contact_data in self.contacts:
                self.create_contact(supplier, contact_data)
            db.commit()

            # 5. After all the data has been transfered
            msgprint("Supplier created successfully with name: {}".format(supplier.supplier_name))
            return supplier
        except Exception as e:
            throw(f"Error creating supplier: {e}")

    def create_address(self, supplier, address_data):
        #create address in address doctype
        address = new_doc("Address")
        address.address_title = supplier.supplier_name  # optional
        address.address_type = "Billing" # You can set address type
        address.address_line1 = address_data.address_line1
        address.address_line2 = address_data.address_line2
        address.city = address_data.city
        address.state = address_data.state
        address.pincode = address_data.pincode
        address.country = address_data.country

        try:
            address.save()
            db.commit()

            #create contact for Supplier
            supplier.append("addresses", { "address_name": address.name })
            supplier.save()
            db.commit()
        except Exception as e:
            throw(f"Error creating address: {e}")

    def create_contact(self, supplier, contact_data):

        contact = new_doc("Contact")
        contact.first_name = contact_data.first_name # Assuming you have this field
        contact.last_name = contact_data.last_name   # Assuming you have this field
        contact.email_id = contact_data.email          # Assuming you have this field
        contact.phone = contact_data.phone          # Assuming you have this field
        contact.is_primary_contact = 1  # mark contact as primary
        try:
            contact.save()
            db.commit()

            #Append the contact name to Supplier contact list
            supplier.append("contacts", { "link": contact.name })

            supplier.save()
            db.commit()
        except Exception as e:
            throw(f"Error creating contact: {e}")