package net.vanevski;

import java.math.BigDecimal;

public class CurrencyApi {
    public static void main(String[] args) {
        if (args.length != 3) {
            System.out.println("Usage: java -jar currapi.jar <FROM> <TO> <AMOUNT>");
            System.out.println("Example: java -jar currapi.jar USD EUR 123.45");
            return;
        }
        String from = args[0];
        String to = args[1];
        String amountStr = args[2];
        BigDecimal amount;
        try {
            amount = new BigDecimal(amountStr);
        } catch (NumberFormatException e) {
            System.err.println("Invalid amount: " + amountStr);
            return;
        }
        try {
            CurrencyConverter converter = new CurrencyConverter();
            BigDecimal converted = converter.convert(from, to, amount);
            System.out.println(amount.stripTrailingZeros().toPlainString() + " " + from.toUpperCase() +
                    " = " + converted.toPlainString() + " " + to.toUpperCase());
        } catch (Exception e) {
            System.err.println("Conversion failed: " + e.getMessage());
        }
    }
}