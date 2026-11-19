from datetime import datetime, timedelta
from collections import UserDict


# Exception class for custom input errors
class InputError(Exception):
    pass


# Base class for record fields
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


# Class for storing contact name
class Name(Field):
    pass


# Class for storing and validating phone number (must be 10 digits)
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


# Class for storing and validating birthday (format: DD.MM.YYYY)
class Birthday(Field):
    def __init__(self, value):
        try:
            # Validate date format and keep value as DD.MM.YYYY string
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


# Class for storing contact information (Name, Phones, Birthday)
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
            return True
        return False

    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError(f"Phone number {old_phone} not found.")
        new_phone_obj = Phone(new_phone)
        index = self.phones.index(phone_obj)
        self.phones[index] = new_phone_obj

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday_date):
        self.birthday = Birthday(birthday_date)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones) if self.phones else "No phones"
        birthday_str = str(self.birthday) if self.birthday else "Not specified"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"


# Class for managing address book records
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            birthday_this_year = birthday_date.replace(year=today.year)

            # If birthday has already passed this year, look at next year
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            # Check if birthday falls within the next 7 days (including today)
            days_until_birthday = (birthday_this_year - today).days

            if 0 <= days_until_birthday <= 7:
                congratulation_date = birthday_this_year
                # If birthday falls on Saturday (5) or Sunday (6), move to Monday
                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                upcoming_birthdays.append({
                    "name": record.name.value,
                    "birthday": congratulation_date.strftime("%d.%m.%Y")
                })

        return upcoming_birthdays


# Decorator for handling input errors gracefully
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError):
            return "Enter user name and required arguments."
        except KeyError:
            return "Contact not found."
        except AttributeError:
            return "Contact not found."
    return inner


# Helper function to parse input text into command and arguments
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


# Command handlers
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error
def show_phones(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record.phones:
        return f"{name}'s phones: {', '.join(p.value for p in record.phones)}"
    return f"No phone numbers stored for {name}."
        


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_date, *_ = args
    record = book.find(name)
    record.add_birthday(birthday_date)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record.birthday:
        return f"{name}'s birthday: {record.birthday.value}"
    return f"No birthday set for {name}."
    


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next 7 days."
    
    result = ["Upcoming birthdays:"]
    for item in upcoming:
        result.append(f"{item['name']}: {item['birthday']}")
    return "\n".join(result)


# Main application loop
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue
            
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phones(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

# --- TEST BLOCK FOR EXCEPTION HANDLING ---
# if __name__ == "__main__":
#     # Initialize AddressBook for testing
#     test_book = AddressBook()
#     print("=== STARTING EXCEPTION TESTS ===\n")

#     # Test 1: IndexError (missing arguments for 'add')
#     print("Test 1 (IndexError): add without arguments")
#     print("Result:", add_contact([], test_book))
#     print("-" * 40)

#     # Test 2: ValueError from Phone validation (invalid phone length/digits)
#     print("Test 2 (ValueError - Phone): add with invalid phone (letters instead of digits)")
#     print("Result:", add_contact(["Alice", "abc1234567"], test_book))
#     print("-" * 40)

#     # Test 3: Successful add to prepare for next tests
#     print("Test 3 (Setup): adding valid contact Alice")
#     print("Result:", add_contact(["Alice", "1234567890"], test_book))
#     print("-" * 40)

#     # Test 4: KeyError (trying to change phone for non-existent contact)
#     print("Test 4 (KeyError): change phone for non-existent contact Bob")
#     print("Result:", change_contact(["Bob", "1234567890", "0987654321"], test_book))
#     print("-" * 40)

#     # Test 5: ValueError from Birthday validation (invalid date format)
#     print("Test 5 (ValueError - Birthday): add-birthday with wrong format (YYYY-MM-DD instead of DD.MM.YYYY)")
#     print("Result:", add_birthday(["Alice", "2000-05-12"], test_book))
#     print("-" * 40)

#     # Test 6: Successful birthday addition
#     print("Test 6 (Setup): add-birthday with correct format")
#     print("Result:", add_birthday(["Alice", "12.05.2000"], test_book))
#     print("-" * 40)

#     # Test 7: add (show birthday for non-existent contact)
#     print("Test 7 (KeyError): show-birthday for non-existent contact Charlie")
#     print("Result:", show_birthday(["Charlie"], test_book))
#     print("\n=== TESTS COMPLETED ===")

