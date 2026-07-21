class ticketCode :
    def checksum(self,ticket) :
        total=0
        for i, ch in enumerate(ticket) :
            #sum add the asci value of each char multiplied by the order 
            # so it depends on both the order and the characters 
            total += (i+1)*ord(ch)
        return total %100 #2 digits 
        

    def encode(self,ticket_id) :
        check=self.checksum(ticket_id)
        return ticket_id + "-" + str(check)
    def decode(self,barcode) :
        try :
            ticket,received = barcode.split("-")
        except ValueError :
            return "CORRUPTED TICKET"
    
        expected= self.checksum(ticket)
        if int(received) == expected :
            return ticket
        else :
            return "CORRUPTED TICKET"
        
codec = ticketCode()

tickets = [
    "MIA2026GATE7",
    "ARGFINAL12",
    "VIP12345"
]
for ticket in tickets:
    barcode = codec.encode(ticket)
    print("Ticket :", ticket)
    print("Barcode:", barcode)
    print("Decoded:", codec.decode(barcode))
    print()


print("Corrupted example")

barcode = codec.encode("MIA2026GATE7")
corrupted = barcode.replace("7", "4", 1)
print("Original :", barcode)
print("Corrupted:", corrupted)
print("Decode:", codec.decode(corrupted))