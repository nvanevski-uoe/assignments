package net.vanevski;

import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Locale;
import java.util.Objects;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Utility to convert currency amounts using a public API.
 * Uses Frankfurter (api.frankfurter.app) which does not require an API key.
 */
public final class CurrencyConverter {
    private static final String API_ENDPOINT = "https://api.frankfurter.app/latest";

    private static final String NUMBER_PATTERN = "[-+]?[0-9]*\\.?[0-9]+(?:[eE][-+]?[0-9]+)?";
    private static final Pattern ERROR_PATTERN = Pattern.compile("\\\"error\\\"\\s*:\\s*\\\"(.*?)\\\"");

    private final HttpClient http;

    public CurrencyConverter() {
        this(HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build());
    }

    public CurrencyConverter(HttpClient http) {
        this.http = Objects.requireNonNull(http);
    }

    /**
     * Converts an amount from one currency to another.
     * @param from ISO 4217 code of source currency (e.g., "USD")
     * @param to ISO 4217 code of target currency (e.g., "EUR")
     * @param amount amount to convert
     * @return converted amount
     * @throws IOException network or API errors
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalArgumentException on invalid inputs or responses
     */
    public BigDecimal convert(String from, String to, BigDecimal amount) throws IOException, InterruptedException {
        validateCurrencyCode(from);
        validateCurrencyCode(to);
        if (amount == null) {
            throw new IllegalArgumentException("amount must not be null");
        }
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("amount must be non-negative");
        }

        String url = String.format(Locale.ROOT, "%s?amount=%s&from=%s&to=%s", API_ENDPOINT,
                amount.stripTrailingZeros().toPlainString(),
                from.toUpperCase(Locale.ROOT), to.toUpperCase(Locale.ROOT));

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .timeout(Duration.ofSeconds(15))
                .GET()
                .build();

        HttpResponse<String> response = http.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 200) {
            throw new IOException("API request failed with status " + response.statusCode());
        }
        String body = response.body();

        // exchangerate.host returns { "success": true, "result": 123.45, ... }
        BigDecimal result = parseConvertedAmount(body, to);
        if (result == null) {
            String apiErr = parseApiError(body);
            if (apiErr != null) {
                throw new IllegalArgumentException("API error: " + apiErr);
            }
            throw new IllegalArgumentException("Could not parse conversion result from API response");
        }
        // Normalize to reasonable scale
        return result.setScale(6, RoundingMode.HALF_UP).stripTrailingZeros();
    }

    private static void validateCurrencyCode(String code) {
        if (code == null || !code.matches("[A-Za-z]{3}")) {
            throw new IllegalArgumentException("Invalid currency code: " + code);
        }
    }

    private static BigDecimal parseConvertedAmount(String json, String toCode) {
        String currency = toCode == null ? "" : toCode.toUpperCase(Locale.ROOT);
        String regex = "\\\"rates\\\"\\s*:\\s*\\{[^}]*\\\"" + Pattern.quote(currency) + "\\\"\\s*:\\s*(" + NUMBER_PATTERN + ")";
        Pattern p = Pattern.compile(regex);
        Matcher m = p.matcher(json);
        if (m.find()) {
            try {
                return new BigDecimal(m.group(1));
            } catch (NumberFormatException ignored) {
                return null;
            }
        }
        return null;
    }

    private static String parseApiError(String json) {
        Matcher m = ERROR_PATTERN.matcher(json);
        if (m.find()) {
            return m.group(1);
        }
        return null;
    }
}
