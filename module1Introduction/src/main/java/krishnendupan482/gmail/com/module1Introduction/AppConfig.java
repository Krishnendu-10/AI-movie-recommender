package krishnendupan482.gmail.com.module1Introduction;


import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {

    @Bean
    public PaymentService paymentService(){
        //more logic
        return new PaymentService();
    }
}
